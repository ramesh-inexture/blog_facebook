from rest_framework import serializers
from .models import Posts, UploadedFiles


class UploadFilesSerializer(serializers.ModelSerializer):
    """ serializer for UploadedFiles Model """
    class Meta:
        model = UploadedFiles
        fields = ['id', 'post_id', 'file']


class PostModelSerializer(serializers.ModelSerializer):
    """ serializer for Posts Model """
    class Meta:
        model = Posts
        fields = ['id', 'title', 'overview', 'description', 'category_id', 'posted_by']


class PostSerializer(serializers.ModelSerializer):
    """ serializer for listing posts with data and files """
    posts_files = UploadFilesSerializer(many=True)

    class Meta:
        model = Posts
        fields = ['id', 'title', 'overview', 'description', 'category_id', 'posted_by', 'posts_files']
        extra_kwargs = {
            'id': {'read_only': True},
            'posted_by': {'read_only': True}
        }


class UpdateDeleteFilesSerializer(serializers.ModelSerializer):
    """ serializer for Update or Delete Files """
    class Meta:
        model = UploadedFiles
        fields = ['id', 'post_id', 'file']
        extra_kwargs = {
            'id': {'read_only': True},
            'post_id': {'read_only': True}
        }


class UpdateDeletePostSerializer(serializers.ModelSerializer):
    """ serializer for Update or Delete Posts """
    class Meta:
        model = Posts
        fields = ['id', 'title', 'overview', 'description', 'category_id', 'posted_by']
        extra_kwargs = {
            'id': {'read_only': True},
            'posted_by': {'read_only': True}
        }



