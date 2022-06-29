from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from authentication.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import User
from .permissions import IsOwner
from django.shortcuts import get_object_or_404
from authentication.serializers import (UserRegistrationSerializer,
    UserLoginSerializer, SendPasswordResetEmailSerializer, UserPasswordResetSerializer, UserProfileSerializer,
    UserChangePasswordSerializer)


def get_tokens_for_user(user):
    """ Generate Token """

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# Registration View for user
class UserRegistrationView(APIView):
    """ User Registration View """

    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({'token': token, 'msg': 'Registration Success'}, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """ User Login View """
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'non_field_errors': ['Email or password is not valid']}},
                            status=status.HTTP_404_NOT_FOUND)


class SendPasswordResetEmailView(APIView):
    """ This View Used in Sending Email to Reset Password (Forgot password) View """

    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)


class UserPasswordResetView(APIView):
    """ After Sending URL for Reset Password This View Handles How to Reset Password by Getting Token and id """

    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset Successfully'},
                        status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    """ Retrieve, Update and Destroy View for Profile in User model To manage Profile Feature of Blog"""

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    # lookup_field = 'pk'

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.request.user.id)
        return obj

    def patch(self, request, *args, **kwargs):
        response = super(UserProfileView, self).partial_update(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Profile updated successfully."},
            status=response.status_code
        )

    def delete(self, request, *args, **kwargs):
        response = super(UserProfileView, self).destroy(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Profile deleted successfully."},
            status=response.status_code
        )


class UserChangePasswordView(APIView):
    """ Change Password View for User """
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Changed Successfully'}, status=status.HTTP_200_OK)
