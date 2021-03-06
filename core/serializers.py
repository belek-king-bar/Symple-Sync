from rest_framework import serializers
from .models import Message, File, Service, Tag, Log


class InlineMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'name', 'url_download')


class MessageSerializer(serializers.ModelSerializer):
    files = InlineMessageSerializer(many=True, read_only=True)
    tag_name = serializers.SerializerMethodField(read_only=True, source='tag')
    service_name = serializers.SerializerMethodField(read_only=True, source='service')

    def get_tag_name(self, message):
        return message.tag.name

    def get_service_name(self, message):
        return message.service.name

    class Meta:
        model = Message
        fields = ('id', 'user', 'tag', 'tag_name', 'service', 'service_name', 'timestamp', 'user_name', 'text',
                  'created_at', 'files')


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ('id', 'user', 'name', 'status', 'last_sync', 'frequency', 'connected')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'user', 'service', 'name')


class LogSerializer(serializers.ModelSerializer):
    service_name = serializers.SerializerMethodField(read_only=True, source='service')

    def get_service_name(self, message):
        return message.service.name

    class Meta:
        model = Log
        fields = ('id', 'service', 'service_name', 'user', 'log_message', 'created_at')
