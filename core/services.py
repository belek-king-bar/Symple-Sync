from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponse
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List
from urllib.request import Request

import os

import pickle

from core.models import Email
from project.settings import SCOPES, CLIENT_CONFIG, CLIENT_TOKEN_LOCATION


class NoEmailFoundError(object):
    pass


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
        list_of_snippets = []
        try:
            messages = response.get('messages', [])
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                snippet = msg['snippet']
                print(type(snippet))
                list_of_snippets.append(snippet)
        except NoEmailFoundError:
            print('No messages found')
        if not messages:
            raise NoEmailFoundError('No messasges found')
        else:
            email = Email(snippet=list_of_snippets)
            email.save()


