from rest_framework import serializers
from .models import Posts, UploadedFiles


class UploadFilesSerializer(serializers.ModelSerializer):

    class Meta:
        model = UploadedFiles
        fields = ['id', 'post_id', 'file']
        # extra_kwargs = {
        #     'id': {'read_only': True},
        #     'post_id': {'read_only': True}
        # }


class PostModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Posts
        fields = ['id', 'title', 'overview', 'description', 'posted_by']
        # extra_kwargs = {
        #     'id': {'read_only': True},
        #     'posted_by': {'read_only': True}
        # }


class PostSerializer(serializers.ModelSerializer):
    posts_files = UploadFilesSerializer(many=True)

    class Meta:
        model = Posts
        fields = ['id', 'title', 'overview', 'description', 'posted_by', 'posts_files']
        extra_kwargs = {
            'id': {'read_only': True},
            'posted_by': {'read_only': True}
        }
        # fields = '__all__'

    # def validate(self, attrs):
    #     posted_by =


class UpdateDeleteFilesSerializer(serializers.ModelSerializer):

    class Meta:
        model = UploadedFiles
        fields = ['id', 'post_id', 'file']
        extra_kwargs = {
            'id': {'read_only': True},
            'post_id': {'read_only': True}
        }


class UpdateDeletePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Posts
        fields = ['id', 'title', 'overview', 'description', 'posted_by']
        extra_kwargs = {
            'id': {'read_only': True},
            'posted_by': {'read_only': True}
        }



