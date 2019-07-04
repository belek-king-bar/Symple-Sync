from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Message, Service, User, Tag
from ..serializers import MessageSerializer

client = Client()


class GetSlackMessagesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='belek', token='1234')
        self.service = Service.objects.create(
            name='slack', status=True, frequency='every day')
        self.service.user.add(self.user.id)

        self.tag = Tag.objects.create(
            name='/ Tag'
        )
        self.tag.user.add(self.user.id), self.tag.service.add(self.service.id)

        self.message = Message.objects.create(
            user=self.user, service=self.service, tag=self.tag, text='/ Tag test'
        )

    def test_get_all_messages(self):
        response = client.get(reverse('slack_message'))
        service = Service.objects.filter(name='slack')
        messages = Message.objects.filter(service=service[0])
        serializer = MessageSerializer(messages, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
