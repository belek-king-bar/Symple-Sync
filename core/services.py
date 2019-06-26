from django.contrib.auth import get_user_model
from django.http import HttpResponse
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List
from urllib.request import Request
from django.db import transaction
import requests
import os
import json
import pickle
from django.conf import settings
from core.models import *
from project.settings import SCOPES, CLIENT_CONFIG

User = get_user_model()


class GoogleService:
  @classmethod
  def get_emails(cls, user: User) -> List[str]:
    creds = None
    if os.path.exists('token.json'):
      with open('token.json', 'rb') as token:
        creds = pickle.load(token)
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG,SCOPES)
        creds = flow.run_local_server()
      with open('token.json', 'wb') as token:
        pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    response = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = response.get('messages', [])
    if not messages:
      return "No messages found."
    else:
      list_of_snippets = []
      for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        snippet = msg['snippet']
        print(type(snippet))
        email = Messages(text=snippet, name='gmail')
        email.save()
    return HttpResponse('done')


class SlackService:
    @classmethod
    @transaction.atomic
    def receive_slack(cls, request):
        channels = []
        groups = []

        service = Services.objects.filter(name='slack')
        service = service[0]
        token = Token.objects.filter(service=service)

        if 'code' in request.GET and not token:
            code = request.GET['code']

            params_to_token = {
              'client_id': settings.CLIENT_ID_SLACK,
              'client_secret': settings.CLIENT_SECRET_SLACK,
              'code': code
            }

            json_response = requests.get(settings.URLS['oauth_access'], params_to_token)
            data = json.loads(json_response.text)
            Token.objects.create(service=service, access_token=data['access_token'])

        elif token:
            access_token = token[0].access_token

            params_to_channel_and_group_list = {
                'token': access_token
            }

            response_channels = requests.get(settings.URLS['channels_list'], params_to_channel_and_group_list)
            data_channel = json.loads(response_channels.text)
            for channel in data_channel['channels']:
                channels.append(channel['id'])

            response_groups = requests.get(settings.URLS['groups_list'], params_to_channel_and_group_list)
            data_groups = json.loads(response_groups.text)
            for group in data_groups['groups']:
                groups.append(group['id'])

            for channel in channels:

                params_to_channels_history = {
                    'token': access_token,
                    'channel': channel
                }

                channels_history = requests.get(settings.URLS['channels_history'], params_to_channels_history)
                data_channels_history = json.loads(channels_history.text)
                tags = Tags.objects.filter(service=service)
                for message in data_channels_history['messages']:
                    for tag in tags:
                        if str(tag) in message['text'] and 'files' in message:
                            data = Messages.objects.create(service=service, tag=tag, text=message['text'],
                                                           user_name=message['user'],
                                                           timestamp=message['files'][0]['timestamp'])

                            data.files.create(name=message['files'][0]['name'],
                                              url_download=message['files'][0]['url_private_download'])

                        elif str(tag) in message['text']:
                            Messages.objects.create(service=service, tag=tag, text=message['text'],
                                                    user_name=message['user'],
                                                    timestamp=message['ts'])

            for group in groups:

                params_to_groups_history = {
                    'token': access_token,
                    'channel': group
                }

                groups_history = requests.get(settings.URLS['groups_history'], params_to_groups_history)
                data_groups_history = json.loads(groups_history.text)
                tags = Tags.objects.filter(service=service)
                for message in data_groups_history['messages']:
                    for tag in tags:
                        if str(tag) in message['text'] and 'files' in message:
                            data = Messages.objects.create(service=service, tag=tag, text=message['text'],
                                                           user_name=message['user'],
                                                           timestamp=message['files'][0]['timestamp'])

                            data.files.create(name=message['files'][0]['name'],
                                              url_download=message['files'][0]['url_private_download'])

                        elif str(tag) in message['text']:
                            Messages.objects.create(service=service, tag=tag, text=message['text'],
                                                    user_name=message['user'],
                                                    timestamp=message['ts'])



