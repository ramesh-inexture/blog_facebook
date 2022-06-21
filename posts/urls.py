from django.urls import path
from .views import (PostCreateAPIView, PostLists, UploadFileAPIView, UpdateDeletePosts,
                    UpdateDeleteFiles, SinglePostListView)

urlpatterns = [
    path('create_posts/', PostCreateAPIView.as_view(), name='create-post'),
    path('upload_file/', UploadFileAPIView.as_view(), name='upload-file'),
    path('post-list/', PostLists.as_view()),
    path('see-post/', SinglePostListView.as_view()),
    path('manage-post/', UpdateDeletePosts.as_view(), name='manage-posts'),
    path('manage-files/', UpdateDeleteFiles.as_view(), name='manage-files'),
]
