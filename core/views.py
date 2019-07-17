import requests
from oauth2client.client import FlowExchangeError
from rest_framework.views import APIView
from core.services import SlackService, GoogleService, OAuthAuthorization, TagsUpdateService
from rest_framework.response import Response
from core.exceptions import NoEmailFoundError, CodeExchangeException, NoDirFoundError, SerializerValidationError
from .serializers import MessageSerializer, ServiceSerializer, TagSerializer, LogSerializer
from .models import Message, Service, User, Tag, Log, Token
from rest_framework import status


class RecieveGmailListView(APIView):
    def get(self, request):
        service = Service.objects.filter(name='gmail')
        messages = Message.objects.filter(service=service.first()).order_by('-created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class SaveGmailListView(APIView):
    def get(self, request):
        try:
            GoogleService.receive_email_messages()
        except NoEmailFoundError:
            return Response({'message': 'No messages found'}, status=404)
        except NoDirFoundError:
            return Response({'message': "This directory doesn't exist"})

        return Response({'message': 'OK'}, status=200)


class ReceiveGmailCodeOauthView(APIView):

    def post(self, request):
        try:
            OAuthAuthorization.gmail_authorization(code=request.data['code'])
        except CodeExchangeException:
            return Response({'message': 'No code found'}, status=401)
        except FlowExchangeError:
            return  Response({'message': 'Invalid auth code'}, status=402 )

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
        messages = Message.objects.filter(service=service.first())
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class ServiceView(APIView):

    def get(self, request):
        services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)

    def put(self, request):
        services = request.data.get('services')
        user = User.objects.first()
        for service in services:
            service_b = Service.objects.get(pk=service['id'])
            token = Token.objects.filter(service=service_b).first()
            if not service['connected'] and service_b.name == 'gmail' and token:
                requests.get('https://accounts.google.com/o/oauth2/revoke?token=%s' % token.access_token)
                token.delete()
                tags = Tag.objects.filter(service=service_b)
                for tag in tags:
                    tag.delete()
            elif not service['connected'] and service_b.name == 'slack' and token:
                token.delete()
                tags = Tag.objects.filter(service=service_b)
                for tag in tags:
                    tag.delete()
            data = {
                'user': [user.id],
                'name': service_b.name,
                'status': service['status'],
                'frequency': service['frequency'],
                'connected': service['connected']
            }

            serializer = ServiceSerializer(service_b, data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)


class TagsView(APIView):

    def get(self, request):
        service = request.GET['service']
        if service:
            service = Service.objects.filter(name=service)
            tags = Tag.objects.filter(service=service.first())
            serializer = TagSerializer(tags, many=True)
            return Response(serializer.data)
        return Response({'message': 'No service found'}, status=404)

    def post(self, request):
        service = Service.objects.get(name=request.data.get('service'))
        new_tags = request.data.get('tags')
        deleted_tags = request.data.get('deletedTags')
        service_tag = Tag.objects.filter(service=service)
        serializer = TagSerializer(service_tag, many=True)
        try:
            TagsUpdateService.tags_update(service, new_tags, deleted_tags)
        except SerializerValidationError:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LogsView(APIView):

    def get(self, request):
        logs = Log.objects.all().order_by('-created_at')
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data)
