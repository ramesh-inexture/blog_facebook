from django.urls import path
from .views import UserRegistrationView, UserLoginView, SendPasswordResetEmailView, UserPasswordResetView, \
    UserChangePasswordView, UserProfileView, BlockUserView, BlockOtherUsersAPIView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('restrict-unrestrict-user/<int:pk>/', BlockUserView.as_view(), name='block-unblock-user-by-admin'),
    path('block-unblock-user/<int:pk>/', BlockOtherUsersAPIView.as_view(), name='block-unblock-by-user'),
]
