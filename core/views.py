from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import NoEmailFoundError
from .serializers import *
from core.services import GoogleService
from rest_framework import generics


class RecieveEmailListView(APIView):
    def get(self, request):
        try:
            emails = GoogleService.receive_emails(request)
            return Response({'message': 'OK'}, status=200)
        except NoEmailFoundError as error:
            return Response({'message': 'No email found'}, status=404)


class EmailView(generics.ListCreateAPIView):
    queryset = Email.objects.all()
    serializer_class = ArraSerialzier

