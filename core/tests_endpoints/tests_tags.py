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

    def test_get_slack_tags(self):
        service = Service.objects.create(
            name='slack_test', status=True, frequency='every day', connected=True)
        service.user.add(self.user.id)
        tag = Tag.objects.create(name='/ Tag')
        tag.user.add(self.user.id)
        tag.service.add(service.id)

        response = client.get(reverse('get_post_tags'), {'service': 'slack_test'})
        service_slack = Service.objects.get(id=service.id)
        tags = Tag.objects.filter(service=service_slack)
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_gmail_tags(self):
        service = Service.objects.create(
            name='gmail_test', status=True, frequency='every day', connected=True)
        service.user.add(self.user.id)
        tag = Tag.objects.create(name='/ Tag')
        tag.user.add(self.user.id)
        tag.service.add(service.id)

        response = client.get(reverse('get_post_tags'), {'service': 'gmail_test'})
        service_gmail = Service.objects.get(id=service.id)
        tags = Tag.objects.filter(service=service_gmail)
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateNewTagTest(TestCase):
    """ Test module for inserting a new puppy """

    def setUp(self):
        self.user = User.objects.create(username='belek', token='1234')
        self.service = Service.objects.create(
            name='slack_test', status=True, frequency='every day', connected=True)
        self.service.user.add(self.user.id)

    def test_create_valid_tags(self):

        valid_payload = {
            "service": 'slack_test',
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
        response = client.post(
            reverse('get_post_tags'),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_tags(self):

        invalid_payload = {
            "service": 'slack_test',
            "tags": [{
                'user': self.user.id,
                'service': self.service.id,
                'name': ''
            }, {
                'user': self.user.id,
                'service': self.service.id,
                'name': ''
            }
            ]
        }
        response = client.post(
            reverse('get_post_tags'),
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateTagsTest(TestCase):
    """ Test module for inserting a new puppy """
    def setUp(self):
        self.user = User.objects.create(username='belek', token='1234')
        self.service = Service.objects.create(
            name='slack_test', status=True, frequency='every day', connected=True)
        self.service.user.add(self.user.id)
        self.tag = Tag.objects.create(name='/ Tag')
        self.tag.user.add(self.user.id)
        self.tag.service.add(self.service.id)

    def test_update_valid_tags(self):

        valid_payload = {
            "service": 'slack_test',
            "tags": [{
                'id': self.tag.id,
                'user': self.user.id,
                'service': self.service.id,
                'name': "/ Tag1"
            }]
        }
        response = client.post(
            reverse('get_post_tags'),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_invalid_tags(self):

        invalid_payload = {
            "service": 'slack_test',
            "tags": [{
                'id': self.tag.id,
                'user': self.user.id,
                'service': self.service.id,
                'name': ''
            }]
        }
        response = client.post(
            reverse('get_post_tags'),
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
