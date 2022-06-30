from rest_framework import serializers
from notifications.models import Notifications


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notifications
        fields = ['notified_user', 'notified_by', 'header', 'body', 'created_at']
