from rest_framework.views import APIView

from core.models import Service, Message
from core.serializers import MessageSerializer
from core.services import SlackService, GoogleService, OAuthAuthorization
from rest_framework.response import Response
from core.exceptions import NoEmailFoundError
from .serializers import MessageSerializer
from .models import Message, Service


class RecieveGmailListView(APIView):
    def get(self, request):
        service = Service.objects.filter(name='gmail')
        messages = Message.objects.filter(service=service[0]).order_by('-created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class SaveGmailListView(APIView):
    def get(self, request):
        try:
            GoogleService.receive_emails(request)
        except NoEmailFoundError as error:
            return Response({'message': 'No messages found'}, status=404)

        return Response({'message': 'ok'}, status=200)


class ReceiveGmailCodeOauthView(APIView):

    def post(self, request):
        try:
            OAuthAuthorization.gmail_authorization(code=request.data['code'])
        except NoEmailFoundError as error:
            return Response({'message': 'No code found'}, status=404)

        return Response({'message': 'OK'}, status=200)


class ReceiveSlackListView(APIView):

    def get(self, request):
        try:
            SlackService.receive_messages()
        except NoEmailFoundError as error:
            return Response({'message': 'No slack found'}, status=404)

        return Response({'message': 'OK'}, status=200)


class ReceiveSlackCodeOauthView(APIView):

    def post(self, request):
        try:
            code = request.data.get('code')
            OAuthAuthorization.slack_authorization(code)
        except NoEmailFoundError as error:
            return Response({'message': 'No code found'}, status=404)

        return Response({'message': 'OK'}, status=200)


class SlackMessageView(APIView):

    def get(self, request):
        service = Service.objects.filter(name='slack')
        messages = Message.objects.filter(service=service[0])
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
