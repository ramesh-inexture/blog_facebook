from django.urls import path
from .views import (PostCreateAPIView, PostLists, UploadFileAPIView, UpdateDeletePosts,
                    UpdateDeleteFiles, SinglePostListView, LikePostView, CommentOnPostView,
                    RetrieveDestroyCommentAPIView, RetrieveDestroyLikeAPIView, TrendingFeedAPIView)

urlpatterns = [
    path('create_posts/', PostCreateAPIView.as_view(), name='create-post'),
    path('upload_file/', UploadFileAPIView.as_view(), name='upload-file'),
    path('post-list/<int:pk>/', PostLists.as_view()),
    path('see-post/', SinglePostListView.as_view()),
    path('manage-post/', UpdateDeletePosts.as_view(), name='manage-posts'),
    path('manage-files/', UpdateDeleteFiles.as_view(), name='manage-files'),
    path('like-post/', LikePostView.as_view(), name='like-post'),
    path('comment-on-post/', CommentOnPostView.as_view(), name='comment-on-post'),
    path('delete-comment-on-post/', RetrieveDestroyCommentAPIView.as_view(), name='delete-comment-on-post'),
    path('remove-like-on-post/', RetrieveDestroyLikeAPIView.as_view(), name='delete-comment-on-post'),
    path('trending-posts/', TrendingFeedAPIView.as_view()),
]
