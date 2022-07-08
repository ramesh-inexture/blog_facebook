from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Friends(models.Model):
    """ This Model will Take Data when Some User Make Friend request to Another user """
    sender_id = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    receiver_id = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE)
    """ It will Check that Users are Friends or Not"""
    is_friend = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} | {self.sender_id} | {self.receiver_id}"
