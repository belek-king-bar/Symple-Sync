from django.contrib.auth import get_user_model
from django.http import HttpResponse
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List
from urllib.request import Request

import os

import pickle

from core.models import Email
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
      # Save the credentials for the next run
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
        list_of_snippets.append(snippet)
      email = Email(snippet=list_of_snippets)
      email.save()
    return HttpResponse('done')