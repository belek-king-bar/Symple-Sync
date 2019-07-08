from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Service, User, Log
from ..serializers import LogSerializer

client = Client()


class GetAllLogsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='belek', token='1234')
        self.service = Service.objects.create(
            name='slack', status=True, frequency='every day')
        self.service.user.add(self.user.id)
        self.log = Log.objects.create(
            user=self.user, service=self.service, log_message='Token successfully received')

    def test_get_all_logs(self):
        response = client.get(reverse('get_logs'))
        logs = Log.objects.all()
        serializer = LogSerializer(logs, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
