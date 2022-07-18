from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import authenticate
from blog.constants import BLOCK_USER, UNBLOCK_USER
from .models import RestrictedUsers
from Friends.models import Friends
from authentication.renderers import UserRenderer
from .models import User
import blog.constants as cons
from .permissions import IsOwner, IsUserActive
from django.shortcuts import get_object_or_404
from authentication.serializers import (UserRegistrationSerializer,
                                        UserLoginSerializer, SendPasswordResetEmailSerializer,
                                        UserPasswordResetSerializer, UserProfileSerializer,
                                        UserChangePasswordSerializer, BlockUserSerializer, BlockUserbyUserSerializer)
from .utils import get_friend_object, get_tokens_for_user


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
    permission_classes = [IsUserActive]

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
    permission_classes = [IsAuthenticated, IsOwner, IsUserActive]

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


class BlockUserView(generics.RetrieveUpdateAPIView):
    """ Admin Can Block Any User Through This EndPoint """
    permission_classes = [IsAdminUser]
    serializer_class = BlockUserSerializer
    queryset = User.objects.all()

    def update(self, request, *args, **kwargs):
        """Updating is_active status of User False To Block the user"""

        data = request.data
        if 'is_active' in data:
            if data['is_active'] == True or data['is_active'].capitalize() == 'T' or data['is_active'].capitalize() ==\
                    'True':
                msg = cons.UNBLOCK_USER
            else:
                msg = cons.BLOCK_USER
        else:
            msg = " 'is_active' Not Changed "
        response = super(BlockUserView, self).update(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": msg},
            status=response.status_code
        )


class BlockOtherUsersAPIView(APIView):
    """This APIView Is Used to Block Other Users from User's End,
    In This View first we get User_id of Main User as Blocked_by and User id Of Other User which want to Block
    Will be Taken as pk From URL when we block any User then They will be Unfriends Automatically"""

    def post(self, request, pk, format=None):
        blocked_by = request.user.id
        if pk == blocked_by:
            raise ValidationError({"Error": "User can Not Block Own Account"})
        data={
            "blocked_by": blocked_by,
            "blocked_user": pk
        }
        friend_obj = get_friend_object(blocked_by,pk)
        if friend_obj:
            sender_id = friend_obj.sender_id_id
            receiver_id = friend_obj.receiver_id_id
            Friends.objects.filter(sender_id=sender_id, receiver_id=receiver_id).delete()

        """If User is Blocked then it will Unblock that User or If User is Not Blocked then it will Block That User"""
        blocked_user_obj = RestrictedUsers.objects.filter(blocked_user=pk,blocked_by=blocked_by)
        if blocked_user_obj:
            blocked_user_obj.delete()
            return Response({'msg': UNBLOCK_USER}, status=status.HTTP_200_OK)

        serializer = BlockUserbyUserSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg':  BLOCK_USER}, status=status.HTTP_200_OK)
