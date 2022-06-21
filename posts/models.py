from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Posts(models.Model):
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    overview = models.TextField(blank=True)
    description = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.posted_by} | {self.id}"


class UploadedFiles(models.Model):
    post_id = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='posts_files')
    file = models.FileField(upload_to=f'posts')

    def __str__(self):
        return f"{self.post_id} | {self.id}"

