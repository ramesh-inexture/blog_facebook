from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from Friends.utils import check_is_friend
from authentication.utils import Util
import blog.constants as cons
from notifications.serializers import NotificationSerializer
from .models import User, Friends
from rest_framework import generics, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from .serializers import (SearchFriendSerializer, MakeFriendRequestSerializer, ListFriendRequestSerializer,
                          ManageFriendRequestSerializer)


class SearchFriendView(generics.ListAPIView):
    """ Search Friend Through This APIView """
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    """ Getting Serializer to Show Data When User Searches Some Other User """
    serializer_class = SearchFriendSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['user_name', 'first_name', 'last_name']


class MakeFriendRequestView(generics.CreateAPIView):
    """ Creating an Endpoint for sending Friend Request to another user"""
    serializer_class = MakeFriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """ Overriding create method to create custom request for add friend endpoint """
        sender_id = request.user.id

        """Getting Data with data fields (mainly receiver_id) from users to create request 
        through data = request.data"""
        data = request.data
        data['sender_id'] = sender_id
        receiver_id = data['receiver_id']

        """ checking that sender_id and receiver_id are same or not if same then raise error or return Response"""
        if str(sender_id) == str(receiver_id):
            return Response({'msg': 'sender_id and receiver_id can not be same'})

        """checking that sender and receiver are friends or sender_id have sent the request to receiver_id
         or sender_id have pending request from receiver_id for restricting sending request again """
        friend_request = check_is_friend(sender_id, receiver_id)
        if friend_request is not None:
            check_for_friends = friend_request[0]
            sender = friend_request[1]
            """ Conditions for different different scenarios of friend request and their status """
            if check_for_friends is True:
                return Response({'msg': f'receiver_id {receiver_id} is Already a Friend'}, status=status.HTTP_400_BAD_REQUEST)
            elif check_for_friends is False and sender == int(sender_id):
                return Response({'msg': 'You have Already sent a friend request'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'msg': 'You have A Pending request from this User'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            """ 
                Making an Serializer for notification For User
                To make Serializer We are Getting Serializer by importing NotificationSerializer from 
                notifications.serializers 
            """
            user_name = request.user.user_name
            obj = User.objects.get(id=receiver_id)
            friend_email = obj.email
            notification_data = {'notified_user': receiver_id, 'notified_by': sender_id, 'header': cons.FRIEND_REQUEST_HEADER,
                        'body': cons.FRIEND_REQUEST_BODY.format(user_name)}
            notification_serializer = NotificationSerializer(data=notification_data)
            if notification_serializer.is_valid():
                notification_serializer.save()
                """ After Saving Data on notification Table we Will Notify User Through Email"""
                notify_data = {
                    'subject': cons.FRIEND_REQUEST_HEADER,
                    'body': cons.FRIEND_REQUEST_BODY.format(user_name),
                    'to_email': friend_email
                }
                Util.send_email(notify_data)
            else:
                return Response({'data': notification_serializer.errors, 'msg': 'Some error has occurred'}, status=status.HTTP_400_BAD_REQUEST)
            """ After Notification Created We will Going To Save Serialized Data of Friend Request """

            serializer.save()
            return Response({
                'status': 200,
                'message': 'Friend Request created',
                'data': serializer.data
            })
        return Response({'data': serializer.errors, 'msg': 'Some error has occurred'})


class SeeFriendRequestView(generics.ListAPIView):
    """ LIST View Of All Pending Friend Requests """
    serializer_class = ListFriendRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        receiver_id = self.request.user.id
        return Friends.objects.filter(receiver_id=receiver_id, is_friend=False)

    def get(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page:
            serializer = ListFriendRequestSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = ListFriendRequestSerializer(queryset, many=True)
            return Response(serializer.data)


class ManageFriendRequestView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ManageFriendRequestSerializer
    permission_classes = [IsAuthenticated]
    """ Here We can Manage Friend Requests Which We have Received From Others"""

    def get_queryset(self):
        user_id = self.request.user.id
        data = self.request.data
        if 'sender_id' in data.keys() and int(data['sender_id']) != int(user_id):
            sender_id = data.get('sender_id')
            receiver_id = user_id
            queryset = Friends.objects.filter(receiver_id=receiver_id, sender_id=sender_id)
            return queryset
        elif 'receiver_id' in data.keys() and int(data['receiver_id']) != int(user_id):
            receiver_id = data.get('receiver_id')
            sender_id = user_id
            queryset = Friends.objects.filter(receiver_id=receiver_id, sender_id=sender_id)
            return queryset
        else:
            return None

    def get_object(self):
        """ getting query_set and creating Obj of user for  managing Friend Requests """
        queryset = self.get_queryset()
        if queryset is None:
            return None
        obj = get_object_or_404(queryset)
        return obj

    def get(self, request, *args, **kwargs):
        """ Over Riding Get Request to Get Data and return Response"""
        obj1 = self.get_object()
        if obj1 is None:
            return Response({"msg": " 'Sender_id' or 'receiver_id' is Required "}, status=status.HTTP_400_BAD_REQUEST)
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        For Accepting Friend Request checking that Friend Request is Accepted or not
        if is_friend Status is Already True means receiver is already a friend and we can not change Friend status
        we can only delete that friend
        """
        user_id = self.request.user.id
        obj1 = self.get_object()
        if obj1 is None:
            return Response({"msg": " 'Sender_id' or 'receiver_id' is Required "}, status=status.HTTP_400_BAD_REQUEST)
        friend_status = obj1.is_friend
        if friend_status is False:
            data = request.data
            if 'receiver_id' in data.keys() and int(data['receiver_id']) != int(user_id):
                return Response({'msg': 'You can Not Accept Your Own Sent Request'}, status=status.HTTP_401_UNAUTHORIZED)
            if 'is_friend' not in data.keys():
                return Response({'msg': " 'is_friend' is required to Accept Friend Request"},
                                status=status.HTTP_400_BAD_REQUEST)
            status_of_friend = request.data['is_friend']
            status_of_friend = status_of_friend.capitalize()
            if str(obj1.is_friend) == str(status_of_friend):
                return Response({'msg': "Update 'is_friend' to True to Accept Request"},
                                status=status.HTTP_400_BAD_REQUEST)
            """ If Request is_friend is False then it will work to make it True """
            sender_id = data['sender_id']
            user_id = request.user.id
            user_name = request.user.user_name
            friend_details = User.objects.get(id=sender_id)
            friend_email = friend_details.email
            response = super(ManageFriendRequestView, self).partial_update(request, *args, **kwargs)
            """ 
                Making an Serializer for notification For User
                To make Serializer We are Getting Serializer by importing NotificationSerializer from 
                notifications.serializers 
            """
            notification_data = {'notified_user': sender_id, 'notified_by': user_id,
                                 'header': cons.FRIEND_REQUEST_HEADER,
                        'body': cons.ACCEPT_FRIEND_REQUEST_BODY.format(user_name)}
            notification_serializer = NotificationSerializer(data=notification_data)
            if notification_serializer.is_valid():
                notification_serializer.save()
                """ After Saving Data on notification Table we Will Notify User Through Email"""
                notify_data = {
                    'subject': cons.FRIEND_REQUEST_HEADER,
                    'body': cons.ACCEPT_FRIEND_REQUEST_BODY.format(user_name),
                    'to_email': friend_email
                }
                Util.send_email(notify_data)
            else:
                return Response({'data': notification_serializer.errors, 'msg': 'Some error has occurred'}, status=status.HTTP_400_BAD_REQUEST)
            """ After Notification Created We will Going To Save Serialized Data of Friend Request """

            return Response(
                {"data": response.data, "message": "Request Accepted."},
                status=response.status_code
            )
        if obj1.is_friend:
            return Response({"msg": "User is Already Your Friend"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"msg": "Not Found"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """deleting file object of provide user_id"""
        response = super(ManageFriendRequestView, self).destroy(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Removed Friend or Friend Request"},
            status=response.status_code
        )
