from rest_framework import serializers

from core.models import Message


class InlineMessageSerializer(object):
    pass


class MessageSerializer(serializers.ModelSerializer):
    tag_name = serializers.SerializerMethodField(read_only=True, source='tag')
    service_name = serializers.SerializerMethodField(read_only=True, source='service')

    def get_tag_name(self, message):
        return message.tag.name

    def get_service_name(self, message):
        return message.service.name

    class Meta:
        model = Message
        fields = ('id', 'user', 'tag', 'tag_name', 'service', 'service_name',
                  'timestamp', 'user_name','text','created_at')
