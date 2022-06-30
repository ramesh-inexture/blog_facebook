from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics
from .serializers import NotificationSerializer
from .models import Notifications


class SeeNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        data = self.request.data
        print(data)
        if 'notified_user' in data.keys():
            notified_user = data.get('notified_user')
            queryset = Notifications.objects.filter(notified_user=notified_user).order_by('-created_at')
            return queryset
        else:
            return None

    def get_object(self):
        queryset = self.get_queryset()
        if queryset is not None:
            obj = get_object_or_404()
        else:
            return Response({'msg': "'notified_user' is a Required Field "})

