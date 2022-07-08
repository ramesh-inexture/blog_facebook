from rest_framework import serializers
from .models import User, Friends


class SearchFriendSerializer(serializers.ModelSerializer):
    """ Serializer For searching Friends """
    class Meta:
        model = User
        fields = ['id', 'user_name', 'first_name', 'last_name']


class MakeFriendRequestSerializer(serializers.ModelSerializer):
    """ Serializer For Make Friend Request """
    class Meta:
        model = Friends
        fields = ['id', 'sender_id', 'receiver_id', 'is_friend']


class ListFriendRequestSerializer(serializers.ModelSerializer):
    """ Serializer For Manage Friend Request """
    class Meta:
        model = Friends
        fields = ['id', 'sender_id', 'receiver_id', 'is_friend']
        extra_kwargs = {
            'id': {'read_only': True},
            'receiver_id': {'read_only': True}
        }


class AllFriendSerializer(serializers.ModelSerializer):
    """ Serializer For getting All Friends"""
    class Meta:
        model = User
        fields = ['id', 'user_name']


class ManageFriendRequestSerializer(serializers.ModelSerializer):
    """ Serializer For Manage Friend Request """

    class Meta:
        model = Friends
        fields = ['id', 'sender_id', 'receiver_id', 'is_friend']
        extra_kwargs = {
            'id': {'read_only': True},
            'receiver_id': {'read_only': True},
        }
