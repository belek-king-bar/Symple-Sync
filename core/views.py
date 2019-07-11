from rest_framework.views import APIView
from core.services import SlackService, GoogleService, OAuthAuthorization
from rest_framework.response import Response
from core.exceptions import NoEmailFoundError
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
            GoogleService.save_emails_to_db(request)
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
            print(service_b)
            print(service['connected'])
            if service['connected'] is False:
                token = Token.objects.filter(service=service_b).first()
                if token:
                    token.delete()
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
        user = User.objects.first()
        service = Service.objects.get(name=request.data.get('service'))
        new_tags = request.data.get('tags')
        deleted_tags = request.data.get('deletedTags')
        if deleted_tags:
            for deleted_tag in deleted_tags:
                tag = Tag.objects.get(pk=deleted_tag)
                tag.delete()

        for new_tag in new_tags:
            if 'id' in new_tag:
                tag = Tag.objects.get(pk=new_tag['id'])
                data = {
                    'user': [user.id],
                    'service': [service.id],
                    'name': new_tag['name'],
                }
                serializer = TagSerializer(tag, data=data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            elif 'id' not in new_tag:
                tags = Tag.objects.filter(service=service)
                names = []
                for tag in tags:
                    names.append(tag.name)
                if new_tag['name'] not in names:
                    data = {
                        'user': [user.id],
                        'service': [service.id],
                        'name': new_tag['name'],
                    }

                    serializer = TagSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        service_tag = Tag.objects.filter(service=service)
        serializer = TagSerializer(service_tag, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LogsView(APIView):

    def get(self, request):
        logs = Log.objects.all().order_by('-created_at')
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data)
