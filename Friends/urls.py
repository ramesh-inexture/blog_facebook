from django.urls import path
from .views import (SearchFriendView, MakeFriendRequestView, ManageFriendRequestView,
                    SeeFriendRequestView, SeeFriendsListAPIView)

urlpatterns = [
    path('search-friend/', SearchFriendView.as_view(), name='search-friend'),
    path('make-friend-request/', MakeFriendRequestView.as_view(), name='friend-request'),
    path('see-friend-requests/', SeeFriendRequestView.as_view(), name='see-friend-request'),
    path('manage-friend-request/', ManageFriendRequestView.as_view(), name='manage-friend-request'),
    path('see-friends-list/', SeeFriendsListAPIView.as_view(), name='see-friends-list'),
]
