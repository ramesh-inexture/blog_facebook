from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()


class Notifications(models.Model):
    notified_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_for')
    notified_by = models.ForeignKey(User, default='Anonymous', on_delete=models.SET_DEFAULT,
                                    related_name='notification_due_to')
    header = models.CharField(max_length=300)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} | notification of {self.header} for {self.notified_user.user_name}"
