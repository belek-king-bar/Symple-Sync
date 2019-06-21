from django.http import HttpResponse

import os
import pickle
from urllib.request import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from project.settings import SCOPES, CLIENT_SECRETS_LOCATION
from .models import Email
# Create your views here.


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
      flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_LOCATION, ' '.join(SCOPES))
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
    return "Putting messagees into DB"
    list_of_snippets = []
    for message in messages:
      msg = service.users().messages().get(userId='me', id=message['id']).execute()
      snippet = msg['snippet']
      list_of_snippets.append(snippet)
    email = Email(snippet=list_of_snippets)
    email.save()
  return HttpResponse("Done")
