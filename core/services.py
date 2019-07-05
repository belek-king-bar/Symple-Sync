import httplib2
import oauth2client
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from django.db import transaction
from core.exceptions import NoEmailFoundError
from core.models import Message, Tag, Token, Service
from project.settings import SCOPES, GOOGLE_REDIRECT_URI, GOOGLE_OAUTH2_CLIENT_SECRETS_JSON, GMAIL_CLIENT_ID, \
    GMAIL_CLIENT_SECRET, GOOGLE_AUTH_URL, GOOGLE_USER_AGENT
from django.conf import settings
import requests
import json


def retrieve_messages(headers):
    delivered_to = None
    date = None
    for i in range(len(headers)):
        if headers[i]['name'] == 'Delivered-To':
            delivered_to = headers[i]['value']
        elif headers[i]['name'] == 'Date':
            date = headers[i]['value']
    return delivered_to, date


class GoogleService:
    @classmethod
    @transaction.atomic
    def receive_emails(cls, request):
        service = Service.objects.filter(name='gmail').first()
        token = Token.objects.filter(service=service)
        tags = Tag.objects.filter(service=service)
        creds = oauth2client.client.GoogleCredentials(token[0].access_token, GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET,
                                                     token[0].refresh_token, None,
                                                      GOOGLE_AUTH_URL,GOOGLE_USER_AGENT)
        http = creds.authorize(httplib2.Http())
        creds.refresh(http)
        gmail_service = build('gmail', 'v1', credentials=creds)
        response = gmail_service.users().messages().list(userId='me', labelIds=[tags.name]).execute()
        messages = response.get('messages', [])
        if not messages:
            raise NoEmailFoundError()
        else:
            for message in messages:
                msg = gmail_service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg['payload']['headers']
                delivered_to, date = retrieve_messages(headers)
                Message.objects.create(service=service, tag=tags, text=msg['snippet'],
                                       user_name=delivered_to, timestamp=date)


class SlackService:
    @classmethod
    def receive_channels(cls):
        channels = []
        service = Service.objects.filter(name='slack')
        service = service[0]
        token = Token.objects.filter(service=service)

        if token:
            access_token = token[0].access_token

            params_to_channel_list = {
                'token': access_token
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
        channels = SlackService.receive_channels()
        service = Service.objects.filter(name='slack')
        token = Token.objects.filter(service=service[0])
        for channel in channels:

            if 'is_channel' in channel:
                url = settings.URLS['channels_history']
            else:
                url = settings.URLS['groups_history']

            params_to_channels_history = {
                'token': token[0].access_token,
                'channel': channel['id']
            }

            channels_history = requests.get(url, params_to_channels_history)
            data_channels_history = json.loads(channels_history.text)
            tags = Tag.objects.filter(service=service[0])
            for message in data_channels_history['messages']:
                for tag in tags:
                    if str(tag) in message['text'] and 'files' in message:
                        data = Message.objects.create(service=service[0], tag=tag, text=message['text'],
                                                      user_name=message['user'],
                                                      timestamp=message['ts'])
                        for file in message['files']:
                            data.files.create(name=file['name'],
                                              url_download=file['url_private_download'])

                    elif str(tag) in message['text'] and 'files' not in message:
                        Message.objects.create(service=service[0], tag=tag, text=message['text'],
                                               user_name=message['user'],
                                               timestamp=message['ts'])


class OAuthAuthorization:
    @classmethod
    def slack_authorization(cls, code):
        service = Service.objects.filter(name='slack')
        token = Token.objects.filter(service=service[0])
        if code and not token:

            params_to_token = {
              'client_id': settings.CLIENT_ID_SLACK,
              'client_secret': settings.CLIENT_SECRET_SLACK,
              'code': code
            }

            json_response = requests.get(settings.URLS['oauth_access'], params_to_token)
            data = json.loads(json_response.text)
            Token.objects.create(service=service[0], access_token=data['access_token'])


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


