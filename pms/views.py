from django.http import HttpResponse
from django.shortcuts import render

import os
import pickle
from urllib.request import Request
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from .models import Email
# Create your views here.

CLIENTSECRETS_LOCATION = 'C:/Users/jagge/workspace/pms_integration/pms/credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
]


def receive_emails(request):
  creds = None
  if os.path.exists('token.json'):
    with open('token.json', 'rb') as token:
      creds = pickle.load(token)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(CLIENTSECRETS_LOCATION, ' '.join(SCOPES))
      creds = flow.run_local_server()
    # Save the credentials for the next run
    with open('token.json', 'wb') as token:
      pickle.dump(creds, token)

  service = build('gmail', 'v1', credentials=creds)

  response = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
  messages = response.get('messages', [])
  if not messages:
    print("No messages found.")
  else:
    print("Message snippets:")
    list_of_snippets = []
    for message in messages:
      msg = service.users().messages().get(userId='me', id=message['id']).execute()
      snippet = msg['snippet']
      list_of_snippets.append(snippet)
    email = Email(snippet=list_of_snippets)
    email.save()
  return HttpResponse("Done")
