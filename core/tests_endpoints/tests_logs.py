from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Service, User, Log
from ..serializers import LogSerializer

client = Client()


class GetAllLogsTest(TestCase):

    def test_get_all_logs(self):
        user = User.objects.create(
            username='belek', token='1234')
        service = Service.objects.create(
            name='slack_test', status=True, frequency='every day', connected=True)
        service.user.add(user.id)
        Log.objects.create(
            user=user, service=service, log_message='Token successfully received')
        response = client.get(reverse('get_logs'))
        logs = Log.objects.all()
        serializer = LogSerializer(logs, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

