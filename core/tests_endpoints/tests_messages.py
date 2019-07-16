from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Message, Service, User, Tag
from ..serializers import MessageSerializer

class GetMessagesTest(TestCase):

    def test_get_slack_messages(self):
        user = User.objects.create(
            username='belek', token='1234')
        service = Service.objects.create(
            name='slack', status=True, frequency='every day', connected=True)
        service.user.add(user.id)

        tag = Tag.objects.create(
            name='/ Tag'
        )
        tag.user.add(user.id), tag.service.add(service.id)

        Message.objects.create(
            user=user, service=service, tag=tag, text='/ Tag test'
        )
        response = client.get(reverse('slack_message'))
        service = Service.objects.filter(name='slack')
        messages = Message.objects.filter(service=service.first())
        serializer = MessageSerializer(messages, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_gmail_messages(self):
        user = User.objects.create(
            username='belek', token='1234')
        service = Service.objects.create(
            name='gmail', status=True, frequency='everyday', connected=True)
        service.user.add(user.id)

        tag = Tag.objects.create(
            name='/ Tag'
        )
        tag.user.add(user.id), tag.service.add(service.id)

        Message.objects.create(
            user=user, service=service, tag=tag, text='/ Tag test'
        )
        response = client.get(reverse('gmail_message'))
        service = Service.objects.filter(name='gmail')
        messages = Message.objects.filter(service=service.first())
        serializer = MessageSerializer(messages, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


client = Client()
