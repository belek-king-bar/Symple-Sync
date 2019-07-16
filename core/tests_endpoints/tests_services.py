import json
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Service, User
from ..serializers import ServiceSerializer


class GetAllServicesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='belek', token='1234')
        self.client = Client()

    def test_get_all_services(self):
        service = Service.objects.create(
            name='slack_test', status=True, frequency='every day', connected=True)
        service.user.add(self.user.id)

        response = self.client.get(reverse('get_put_services'))
        services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UpdateServiceTest(TestCase):
    """ Test module for inserting a new puppy """

    def setUp(self):
        self.user = User.objects.create(username='belek', token='1234')
        self.service = Service.objects.create(
            name='slack_test', status=True, frequency='every day', connected=True)
        self.service.user.add(self.user.id)
        self.client = Client()

    def test_update_valid_service(self):

        valid_payload = {
            'services': [{
                "id": self.service.id,
                "name": "slack_test",
                "status": True,
                "frequency": "every month",
                'connected': True
            }]
        }

        response = self.client.put(
            reverse('get_put_services'),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_invalid_service(self):

        invalid_payload = {
            'services': [{
                "id": self.service.id,
                "name": "slack_test",
                "status": '',
                "frequency": "every month",
                'connected': True
            }]
        }
        response = self.client.put(
            reverse('get_put_services'),
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
