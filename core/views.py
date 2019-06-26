from rest_framework.views import APIView
from core.services import GoogleService, SlackService
from django.http import HttpResponse
from rest_framework.response import Response
from core.exceptions import NoEmailFoundError
from rest_framework import viewsets
from .serializers import *


class RecieveEmailListView(APIView):

    def get(self, request):
        emails = GoogleService.get_emails(request)
        return HttpResponse(emails)


class ReceiveSlackListView(APIView):

    def get(self, request):
        try:
            SlackService.receive_slack(request)
        except NoEmailFoundError as error:
            return Response({'message': 'No email found'}, status=404)

        return Response({'message': 'OK'}, status=200)



