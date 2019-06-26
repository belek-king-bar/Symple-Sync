from rest_framework.views import APIView
from rest_framework import generics
from core.services import GoogleService, SlackService
from rest_framework.response import Response
from core.exceptions import NoEmailFoundError
from .serializers import *


class RecieveEmailListView(APIView):
    def get(self, request):
        try:
            emails = GoogleService.receive_emails(request)
        except NoEmailFoundError as error:
            return Response({'message': 'No email found'}, status=404)

        return Response({'message': 'OK'}, status=200)

class EmailView(generics.ListCreateAPIView):
    queryset = Email.objects.all()
    serializer_class = ArraSerialzier


class ReceiveSlackListView(APIView):

    def get(self, request):
        try:
            SlackService.receive_slack(request)
        except NoEmailFoundError as error:
            return Response({'message': 'No email found'}, status=404)

        return Response({'message': 'OK'}, status=200)



