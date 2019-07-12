import base64
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from django.db import transaction
from core.constants import EVERYDAY, EVERY_MONTH, DAY, MONTH, EVERY_WEEK, WEEK
from core.exceptions import NoEmailFoundError
from core.models import Message, Tag, Token, Service, User, Log
from core.serializers import ServiceSerializer
from core.utils import store_to_s3
from project.settings import SCOPES, GOOGLE_REDIRECT_URI, GOOGLE_OAUTH2_CLIENT_SECRETS_JSON, GMAIL_CLIENT_ID, \
    GMAIL_CLIENT_SECRET, GOOGLE_AUTH_URL, GOOGLE_USER_AGENT, STORE_DIR
from django.conf import settings
from datetime import datetime, timedelta
import requests
import json
import httplib2
import oauth2client


class GoogleService:
    @classmethod
    def retrieve_messages(cls, headers):
        delivered_to = None
        date = None
        for i in range(len(headers)):
            if headers[i]['name'] == 'Delivered-To':
                delivered_to = headers[i]['value']
            elif headers[i]['name'] == 'Date':
                date = headers[i]['value']
        return delivered_to, date

    @classmethod
    def retrieve_files(cls, msg, gmail_service, message):
        url = None
        file_name = None
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['filename']:
                    file_name = part['filename']
                    if 'data' in part['body']:
                        data = part['body']['data']
                    else:
                        att_id = part['body']['attachmentId']
                        att = gmail_service.users().messages().attachments().get(userId='me', messageId=message['id'],
                                                                                 id=att_id).execute()
                        data = att['data']
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                    path = STORE_DIR + file_name
                    f = open(path, 'wb')
                    f.write(file_data)
                    f.close()
                    url = store_to_s3(path, file_name)
        return url, file_name

    @classmethod
    def retrieve_label_id(cls, gmail_service, tag):
        response = gmail_service.users().labels().list(userId='me').execute()
        labels = response['labels']
        label_id = None
        for label in labels:
            if label['name'] == tag.name:
                label_id = label['id']
        return label_id

    @classmethod
    @transaction.atomic
    def save_emails_to_db(cls, request):
        service = Service.objects.filter(name='gmail').first()
        token = Token.objects.filter(service=service).first()
        tags = Tag.objects.filter(service=service)
        creds = oauth2client.client.GoogleCredentials(token.access_token, GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET,
                                                     token.refresh_token, None,
                                                      GOOGLE_AUTH_URL,GOOGLE_USER_AGENT)
        http = creds.authorize(httplib2.Http())
        creds.refresh(http)
        gmail_service = build('gmail', 'v1', credentials=creds)
        for tag in tags:
            label_id = GoogleService.retrieve_label_id(gmail_service, tag)
            response = gmail_service.users().messages().list(userId='me', labelIds=[label_id]).execute()
            messages = response.get('messages', [])
            if not messages:
                raise NoEmailFoundError()
            else:
                for message in messages:
                    msg = gmail_service.users().messages().get(userId='me', id=message['id']).execute()
                    headers = msg['payload']['headers']
                    delivered_to, date = GoogleService.retrieve_messages(headers)
                    url, file_name = GoogleService.retrieve_files(msg, gmail_service, message)
                    if file_name is None and url is None:
                        Message.objects.create(service=service, tag=tag, text=msg['snippet'],
                                               user_name=delivered_to, timestamp=date)
                    elif file_name is not None and url is not None:
                        message = Message.objects.create(service=service, tag=tag, text=msg['snippet'],
                                               user_name=delivered_to, timestamp=date)
                        message.files.create(name=file_name, url_download=url)


class SlackService:
    @classmethod
    def receive_channels(cls, token):
        channels = []

        params_to_channel_list = {
            'token': token
        }

        response_channels = requests.get(settings.URLS['channels_list'], params_to_channel_list)
        data_channel = json.loads(response_channels.text)
        for channel in data_channel['channels']:
            channels.append(channel)

        response_groups = requests.get(settings.URLS['groups_list'], params_to_channel_list)
        data_groups = json.loads(response_groups.text)
        for group in data_groups['groups']:
            channels.append(group)

        return channels

    @classmethod
    def receive_messages(cls):
        service = Service.objects.filter(name='slack').first()
        token = Token.objects.filter(service=service)
        user = User.objects.first()
        if token and service.status:
            Log.objects.create(user=user, service=service,
                               log_message='Synchronization successfully started')
            token = token.first().access_token
            channels = SlackService.receive_channels(token)
            count_message = 0
            for channel in channels:

                if 'is_channel' in channel:
                    url = settings.URLS['channels_history']
                else:
                    url = settings.URLS['groups_history']

                params_to_channels_history = {
                    'token': token,
                    'channel': channel['id']
                }

                channels_history = requests.get(url, params_to_channels_history)
                data_channels_history = json.loads(channels_history.text)
                date = SlackService.get_date(service.frequency)
                date_ts = datetime.timestamp(date)
                for message in data_channels_history['messages']:
                    if float(message['ts']) > date_ts:
                        count = SlackService.save_messages_to_base(message_in=message, service=service, user=user)
                        count_message += count

            Log.objects.create(user=user, service=service,
                               log_message='Successfully added %s messages' % count_message)
        else:
            Log.objects.create(user=user, service=service, log_message='Synchronization error')

    @classmethod
    def save_messages_to_base(cls, message_in, service, user):
        count = 0
        client_msg_id = []
        tags = Tag.objects.filter(service=service)
        messages = Message.objects.filter(service=service)
        for message in messages:
            client_msg_id.append(message.message_id)
        for tag in tags:
            if tag.name in message_in['text'] and 'files' in message_in and message_in['client_msg_id']\
                    not in client_msg_id:
                value_datetime = datetime.fromtimestamp(float(message_in['ts']))
                username = SlackService.receive_username(message_in['user'])
                data = Message.objects.create(user=user, service=service, tag=tag, text=message_in['text'],
                                              user_name=username, timestamp=value_datetime,
                                              message_id=message_in['client_msg_id'])
                for file in message_in['files']:
                    data.files.create(name=file['name'],
                                      url_download=file['url_private_download'])

                count += 1

            elif tag.name in message_in['text'] and 'files' not in message_in and message_in['client_msg_id']\
                    not in client_msg_id:
                value_datetime = datetime.fromtimestamp(float(message_in['ts']))
                username = SlackService.receive_username(message_in['user'])
                Message.objects.create(user=user, service=service, tag=tag, text=message_in['text'],
                                       user_name=username,
                                       timestamp=value_datetime, message_id=message_in['client_msg_id'])
                count += 1
        SlackService.save_last_sync(service)
        return count

    @classmethod
    def get_date(cls, frequency):
        date = datetime.now()
        if frequency == EVERYDAY:
            date -= timedelta(days=DAY)
        elif frequency == EVERY_MONTH:
            date -= timedelta(days=MONTH)
        elif frequency == EVERY_WEEK:
            date -= timedelta(days=WEEK)
        return date

    @classmethod
    def save_last_sync(cls, service):
        user = User.objects.first()
        data = {
            "user": [user.id],
            "name": service.name,
            "status": service.status,
            "last_sync": datetime.now()
        }

        serializer = ServiceSerializer(service, data=data)
        if serializer.is_valid():
            serializer.save()

    @classmethod
    def receive_username(cls, user_id):
        service = Service.objects.filter(name='slack')
        service = service.first()
        token = Token.objects.filter(service=service)

        if token:
            access_token = token.first().access_token

            params_to_username = {
                'token': access_token,
                'user': user_id
            }

            response = requests.get(settings.URLS['username'], params_to_username)
            username = json.loads(response.text)
            user = username['user']['real_name']
            return user


class OAuthAuthorization:
    @classmethod
    def slack_authorization(cls, code):
        service = Service.objects.filter(name='slack')
        service = service.first()
        token = Token.objects.filter(service=service)
        user = User.objects.first()
        if code and not token:
            params_to_token = {
              'client_id': settings.CLIENT_ID_SLACK,
              'client_secret': settings.CLIENT_SECRET_SLACK,
              'code': code
            }

            json_response = requests.get(settings.URLS['oauth_access'], params_to_token)
            data = json.loads(json_response.text)
            Token.objects.create(service=service, access_token=data['access_token'])
            Log.objects.create(user=user, service=service, log_message='Authorized successfully')
            data = {
                'user': [user.id],
                'name': service.name,
                'status': service.status,
                'frequency': service.frequency,
                'connected': True
            }
            serializer = ServiceSerializer(service, data=data)
            if serializer.is_valid():
                serializer.save()
        else:
            Log.objects.create(user=user, service=service, log_message='Authorization error')

    @classmethod
    def gmail_authorization(cls, code):
        service = Service.objects.filter(name='gmail').first()
        token = Token.objects.filter(service=service)
        if code and not token:
            exchange_token = code
            flow = flow_from_clientsecrets(GOOGLE_OAUTH2_CLIENT_SECRETS_JSON, ' '.join(SCOPES))
            flow.redirect_uri = GOOGLE_REDIRECT_URI
            credentials = flow.step2_exchange(exchange_token)
            Token.objects.create(service=service, access_token=credentials.access_token,
                                 refresh_token=credentials.refresh_token)
