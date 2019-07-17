from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Service, User, Log
from ..serializers import LogSerializer


class GetAllLogsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='belek', token='1234')
        self.client = Client()


    def test_get_all_logs(self):
        service = Service.objects.create(
            name='slack_test', status=True, frequency='every day', connected=True)
        service.user.add(self.user.id)
        Log.objects.create(
            user=self.user, service=service, log_message='Token successfully received')
        response = self.client.get(reverse('get_logs'))
        logs = Log.objects.all()
        serializer = LogSerializer(logs, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

