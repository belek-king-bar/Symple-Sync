from django.http import HttpResponse
from rest_framework.views import APIView
from .serializers import *
from core.services import GoogleService
from rest_framework import generics


class RecieveEmailListView(APIView):
    def get(self, request):
        emails = GoogleService.receive_emails(request)
        return HttpResponse(emails)

class EmailView(generics.ListCreateAPIView):
    queryset = Email.objects.all()
    serializer_class = ArraSerialzier

