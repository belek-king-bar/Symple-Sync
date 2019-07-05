import json
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Service, User
from ..serializers import ServiceSerializer

client = Client()


class GetAllServicesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='belek', token='1234')
        self.service = Service.objects.create(
            name='slack', status=True, frequency='every day')
        self.service.user.add(self.user.id)

    def test_get_all_services(self):
        # get API response
        response = client.get(reverse('get_post_services'))
        services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateNewServiceTest(TestCase):
    """ Test module for inserting a new puppy """

    def setUp(self):
        self.user = User.objects.create(id=2,
                                        username='belek', token='1234')
        self.service = Service.objects.create(
            name='slack', status=True, frequency='every day')
        self.service.user.add(self.user.id)
        print(self.user.id)
        self.valid_payload = {
            'user': self.user.id,
            'name': "google_drive",
            'status': True,
            'last_sync': '2019-07-03 06:13:14.064174',
            'frequency': 'every day'
        }

        self.invalid_payload = {
            'user': self.user.id,
            'name': "google_drive",
            'status': '',
            'last_sync': '2019-07-03 06:13:14.064174',
            'frequency': 'every day'
        }

    def test_create_valid_service(self):
        response = client.post(
            reverse('get_post_services'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_service(self):
        response = client.post(
            reverse('get_post_services'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateServiceTest(TestCase):
    """ Test module for inserting a new puppy """

    def setUp(self):
        self.user = User.objects.create(id=2,
                                        username='belek', token='1234')
        self.service = Service.objects.create(
            name='slack', status=True, frequency='every day')
        self.service.user.add(self.user.id)

        self.valid_payload = {
            'services': [{
                "id": self.service.id,
                "name": "slack",
                "status": True,
                "frequency": "every month"
            }]
        }

        self.invalid_payload = {
            'services': [{
                "id": self.service.id,
                "name": "slack",
                "status": '',
                "frequency": "every month"
            }]
        }

    def test_update_valid_service(self):
        response = client.put(
            reverse('get_post_services'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_invalid_service(self):
        response = client.put(
            reverse('get_post_services'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
