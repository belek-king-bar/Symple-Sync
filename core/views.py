from rest_framework.views import APIView
from core.services import SlackService, GoogleService, OAuthAuthorization
from rest_framework.response import Response
from core.exceptions import NoEmailFoundError
from .serializers import MessageSerializer, ServiceSerializer
from .models import Message, Service, User
from rest_framework import status


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


class ServiceView(APIView):

    def get(self, request):
        services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = User.objects.get(pk=2)

        data = {
            'user': [user.id],
            'name': request.data.get('name'),
            'status': request.data.get('status'),
            'frequency': request.data.get('frequency')
        }

        serializer = ServiceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        services = request.data.get('services')
        user = User.objects.get(pk=2)
        for service in services:
            service_b = Service.objects.get(pk=service['id'])

            data = {
                'user': [user.id],
                'name': service_b.name,
                'status': service['status'],
                'frequency': service['frequency']
            }

            serializer = ServiceSerializer(service_b, data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)
