from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from urllib.request import Request
from django.db import transaction
from core.exceptions import NoEmailFoundError
from core.models import Message, Tag, Token, Service
from project.settings import SCOPES, CLIENT_CONFIG, CLIENT_TOKEN_LOCATION
from django.conf import settings
import requests
import os
import json
import pickle


class GoogleService:
    @classmethod
    @transaction.atomic
    def receive_emails(cls, request):
        creds = None
        if os.path.exists(CLIENT_TOKEN_LOCATION):
            with open(CLIENT_TOKEN_LOCATION, 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
                creds = flow.run_local_server()
            with open(CLIENT_TOKEN_LOCATION, 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)

        response = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        messages = response.get('messages', [])
        if not messages:
            raise NoEmailFoundError()
        else:
            list_of_snippets = []
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                snippet = msg['snippet']
                email = Message(text=snippet)
                email.save()


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
                        for file in message['files']:
                            data = Message.objects.create(service=service[0], tag=tag, text=message['text'],
                                                          user_name=message['user'],
                                                          timestamp=file['timestamp'])

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
