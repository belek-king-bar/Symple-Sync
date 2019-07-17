from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Message, Service, User, Tag
from ..serializers import MessageSerializer

class GetMessagesTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='belek', token='1234')
        self.client = Client()

    def test_get_slack_messages(self):
        service = Service.objects.create(
            name='slack', status=True, frequency='every day', connected=True)
        service.user.add(self.user.id)

        tag = Tag.objects.create(
            name='/ Tag'
        )
        tag.user.add(self.user.id), tag.service.add(service.id)

        Message.objects.create(
            user=self.user, service=service, tag=tag, text='/ Tag test'
        )
        response = self.client.get(reverse('slack_message'))
        service = Service.objects.filter(name='slack')
        messages = Message.objects.filter(service=service.first())
        serializer = MessageSerializer(messages, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_gmail_messages(self):
        service = Service.objects.create(
            name='gmail', status=True, frequency='everyday', connected=True)
        service.user.add(self.user.id)

        tag = Tag.objects.create(
            name='/ Tag'
        )
        tag.user.add(self.user.id), tag.service.add(service.id)

        Message.objects.create(
            user=self.user, service=service, tag=tag, text='/ Tag test'
        )
        response = self.client.get(reverse('gmail_message'))
        service = Service.objects.filter(name='gmail')
        messages = Message.objects.filter(service=service.first())
        serializer = MessageSerializer(messages, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
