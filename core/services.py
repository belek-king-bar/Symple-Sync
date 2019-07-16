from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from core.exceptions import NoEmailFoundError, CodeExchangeException, NoDirFoundError
from oauth2client.client import flow_from_clientsecrets
from core.models import Message, Tag, Token, Service, User, Log
from core.serializers import ServiceSerializer
from core.utils import store_to_s3
from core.constants import TIMESTAMP_WITH_UTC, EVERY_MONTH, EVERY_WEEK, EVERYDAY, LOCAL, TIMESTAMP_WITHOUT_UTC, DAY, \
    MONTH, WEEK
from project.settings import SCOPES, GOOGLE_REDIRECT_URI, GOOGLE_OAUTH2_CLIENT_SECRETS_JSON, CLIENT_ID_GMAIL, \
    CLIENT_SECRET_GMAIL, GOOGLE_AUTH_URL, USER_AGENT, STORE_DIR
from django.conf import settings
from datetime import datetime, timedelta
import requests
import json
import httplib2
import oauth2client
import base64


class GoogleService:
    @classmethod
    def retrieve_username_and_date(cls, headers):
        delivered_to = None
        timestamp = None
        for header in headers:
            if header['name'] == 'Delivered-To':
                delivered_to = header['value']
            elif header['name'] == 'Date':
                timestamp = header['value']
        return delivered_to, timestamp

    @classmethod
    def retrieve_files(cls, msg, gmail_service, email_message):
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
                        att = gmail_service.users().messages().attachments().get(userId='me', messageId=email_message['id'],
                                                                                 id=att_id).execute()
                        data = att['data']
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                    path = STORE_DIR + file_name
                    if path:
                        f = open(path, 'wb')
                        f.write(file_data)
                        f.close()
                        url = store_to_s3(path, file_name)
                    else:
                        raise NoDirFoundError
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
    def save_emails_to_db(cls, service, gmail_service, tag, email_messages, user):
        count = 0
        messages = Message.objects.filter(service=service)
        client_email_message_id = []
        for message in messages:
            client_email_message_id.append(message.message_id)
        date_frequency = SlackService.get_date(service.frequency)
        local_date_frequency = LOCAL.localize(date_frequency, is_dst=None)
        for email_message in email_messages:
            if email_message['id'] not in client_email_message_id:
                msg = gmail_service.users().messages().get(userId='me', id=email_message['id']).execute()
                headers = msg['payload']['headers']
                delivered_to, timestamp = GoogleService.retrieve_username_and_date(headers)
                if len(timestamp) < TIMESTAMP_WITHOUT_UTC:
                    date = datetime.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %z")
                elif len(timestamp) > TIMESTAMP_WITH_UTC:
                    date = datetime.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %z (%Z)")
                url, file_name = GoogleService.retrieve_files(msg, gmail_service, email_message)
                if date > local_date_frequency:
                    if file_name is None and url is None:
                        Message.objects.create(service=service, tag=tag, text=msg['snippet'],
                                               user_name=delivered_to, timestamp=timestamp,
                                               message_id=email_message['id'], user=user)
                        count += 1
                    elif file_name is not None and url is not None:
                        message = Message.objects.create(service=service, tag=tag, text=msg['snippet'],
                                                         user_name=delivered_to, timestamp=date,
                                                         message_id=email_message['id'], user=user)
                        message.files.create(name=file_name, url_download=url)
                        count += 1
                SlackService.save_last_sync(service)
        return count

    @classmethod
    def receive_email_messages(cls):
        count_message = 0
        user = User.objects.first()
        service = Service.objects.filter(name='gmail').first()
        token = Token.objects.filter(service=service).first()
        tags = Tag.objects.filter(service=service)
        creds = oauth2client.client.GoogleCredentials(token.access_token, CLIENT_ID_GMAIL, CLIENT_SECRET_GMAIL,
                                                      token.refresh_token, None,
                                                      GOOGLE_AUTH_URL, USER_AGENT)
        http = creds.authorize(httplib2.Http())
        creds.refresh(http)
        gmail_service = build('gmail', 'v1', credentials=creds)
        for tag in tags:
            label_id = GoogleService.retrieve_label_id(gmail_service, tag)
            response = gmail_service.users().messages().list(userId='me', labelIds=[label_id]).execute()
            email_messages = response.get('messages', [])
            if not email_messages:
                Log.objects.create(user=user, service=service, log_message='Synchronization error')
                raise NoEmailFoundError()
            else:
                count = GoogleService.save_emails_to_db(service, gmail_service, tag, email_messages, user)
                count_message += count
                Log.objects.create(user=user, service=service,
                                   log_message='Successfully added %s messages' % count_message)


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
        user = User.objects.first()
        if code and not token:
            flow = flow_from_clientsecrets(GOOGLE_OAUTH2_CLIENT_SECRETS_JSON, ' '.join(SCOPES))
            flow.redirect_uri = GOOGLE_REDIRECT_URI
            try:
                credentials = flow.step2_exchange(code)
                Token.objects.create(service=service, access_token=credentials.access_token,
                                     refresh_token=credentials.refresh_token)
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
            except:
                Log.objects.create(user=user, service=service, log_message='Authorization error')
                raise FlowExchangeError()
        else:
            raise CodeExchangeException()
