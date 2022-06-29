from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PostCategories(models.Model):
    """ Creating model for  Post Categories for Uploaded Posts """
    category = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.id} | {self.category}"


class Posts(models.Model):
    """ Post model for Posting Blog Posts"""
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    is_public = models.BooleanField(default=False)
    overview = models.TextField(blank=True)
    description = models.TextField(blank=True)
    category_id = models.ForeignKey(PostCategories, null=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} | {self.posted_by}"


class Likes(models.Model):
    """ Like on A Post by friend is Stored through this Likes Model """
    post_id = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='post_like')
    liked_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.id} | {self.liked_by} Liked a post named {self.post_id.title}'


class Comments(models.Model):
    """ Comments Model for Comments in Posts"""
    post_id = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='post_comment')
    commented_by = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default='anonymous')
    comment = models.TextField(max_length=300, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.id }| Commented by {self.commented_by} on {self.post_id.title}'


class UploadedFiles(models.Model):
    """ Uploaded file will be stored through this UploadFiles model"""
    post_id = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='posts_files')
    file = models.FileField(upload_to=f'posts')

    def __str__(self):
        return f"{self.id} | {self.post_id}"





