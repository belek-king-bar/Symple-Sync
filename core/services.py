from django.db import transaction
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from urllib.request import Request

import os

import pickle

from core.exceptions import NoEmailFoundError
from core.models import Email
from project.settings import SCOPES, CLIENT_CONFIG, CLIENT_TOKEN_LOCATION


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
                list_of_snippets.append(snippet)
            email = Email(snippet=list_of_snippets)
            email.save()

