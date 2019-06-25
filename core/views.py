from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from core.services import GoogleService
from rest_framework import generics, status


class NoEmailFoundError(object):
    pass


class RecieveEmailListView(APIView):
    def get(self, request):
        try:
            emails = GoogleService.receive_emails(request)
        except NoEmailFoundError() as error:
            return Response({'message': 'No email found'}, status=404)


class EmailView(generics.ListCreateAPIView):
    queryset = Email.objects.all()
    serializer_class = ArraSerialzier

