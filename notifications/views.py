from rest_framework.permissions import IsAuthenticated
from authentication.permissions import IsUserActive
from rest_framework import generics
from .serializers import NotificationSerializer
from .models import Notifications


class SeeNotificationsView(generics.ListAPIView):
    """ This feature is used to see all the notification of the authenticated User """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsUserActive]

    def get_queryset(self):
        """ getting User_id to get Obj of Notifications For that User and returns queryset and
        automatically create obj of queryset"""
        notified_user = self.request.user.id
        queryset = Notifications.objects.filter(notified_user=notified_user).order_by('-created_at')
        return queryset
