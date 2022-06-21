from django.urls import path
from .views import UserRegistrationView, UserLoginView, SendPasswordResetEmailView, UserPasswordResetView, \
    UserChangePasswordView, UserProfileView
# from rest_framework.routers import DefaultRouter
#
# router = DefaultRouter()
# router.register('profileapi', UpdateProfileView, basename='profile')


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
]
