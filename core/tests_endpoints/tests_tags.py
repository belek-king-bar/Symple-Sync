import json
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Service, User, Tag
from ..serializers import TagSerializer

client = Client()


class GetAllTagsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='belek', token='1234')
        self.service = Service.objects.create(
            name='slack', status=True, frequency='every day')
        self.service.user.add(self.user.id)
        self.service2 = Service.objects.create(
            name='gmail', status=True, frequency='every day')
        self.service2.user.add(self.user.id)
        self.tag = Tag.objects.create(name='/ Tag')
        self.tag.user.add(self.user.id)
        self.tag.service.add(self.service.id)

    def test_get_slack_tags(self):
        # get API response
        response = client.get(reverse('get_post_tags'), {'service': 'slack'})
        service_slack = Service.objects.get(id=self.service.id)
        tags = Tag.objects.filter(service=service_slack)
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_gmail_tags(self):
        # get API response
        response = client.get(reverse('get_post_tags'), {'service': 'gmail'})
        service_gmail = Service.objects.get(id=self.service2.id)
        tags = Tag.objects.filter(service=service_gmail)
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateNewTagTest(TestCase):
    """ Test module for inserting a new puppy """

    def setUp(self):
        self.user = User.objects.create(username='belek', token='1234')
        self.service = Service.objects.create(
            name='slack', status=True, frequency='every day')
        self.service.user.add(self.user.id)

        self.valid_payload = {
            "service": 'slack',
            "tags": [{
                'user': self.user.id,
                'service': self.service.id,
                'name': "/ Tag1",
            }, {
                'user': self.user.id,
                'service': self.service.id,
                'name': "/ Tag2"
            }
            ]
        }

        self.invalid_payload = {
            "service": 'slack',
            "tags": [{
                'user': self.user.id,
                'service': self.service.id,
                'name': "",
            }, {
                'user': self.user.id,
                'service': self.service.id,
                'name': ""
            }
            ]
        }

    def test_create_valid_tags(self):
        response = client.post(
            reverse('get_post_tags'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_tags(self):
        response = client.post(
            reverse('get_post_tags'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateTagsTest(TestCase):
    """ Test module for inserting a new puppy """

    def setUp(self):
        self.user = User.objects.create(username='belek', token='1234')
        self.service = Service.objects.create(
            name='slack', status=True, frequency='every day')
        self.service.user.add(self.user.id)
        self.tag = Tag.objects.create(name='/ Tag')
        self.tag.user.add(self.user.id)
        self.tag.service.add(self.service.id)

        self.valid_payload = {
            "service": 'slack',
            "tags": [{
                'id': self.tag.id,
                'user': self.user.id,
                'service': self.service.id,
                'name': "/ Tag1"
            }]
        }

        self.invalid_payload = {
            "service": 'slack',
            "tags": [{
                'id': self.tag.id,
                'user': self.user.id,
                'service': self.service.id,
                'name': ""
            }]
        }

    def test_update_valid_tags(self):
        response = client.post(
            reverse('get_post_tags'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_invalid_tags(self):
        response = client.post(
            reverse('get_post_tags'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
