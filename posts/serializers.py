from rest_framework import serializers
from .models import Posts, UploadedFiles, Likes, Comments


class UploadFilesSerializer(serializers.ModelSerializer):
    """ serializer for UploadedFiles Model """

    class Meta:
        model = UploadedFiles
        fields = ['id', 'post_id', 'file']


class PostModelSerializer(serializers.ModelSerializer):
    """ serializer for Posts Model """

    class Meta:
        model = Posts
        fields = ['id', 'title', 'overview', 'description', 'category_id', 'is_public', 'posted_by']


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
        fields = ['id', 'title', 'overview', 'description', 'is_public', 'category_id', 'posted_by']
        extra_kwargs = {
            'id': {'read_only': True},
            'posted_by': {'read_only': True}
        }


class LikePostSerializer(serializers.ModelSerializer):
    """ Serializer for Like Posts Of Friends """

    class Meta:
        model = Likes
        fields = ['id', 'post_id', 'liked_by', 'created_at']


class CommentOnPostSerializer(serializers.ModelSerializer):
    """ Serializer for Comment On Posts Of Friends """

    class Meta:
        model = Comments
        fields = ['id', 'post_id', 'commented_by', 'comment', 'created_at']


class TrendingFeedsSerializer(serializers.ModelSerializer):
    """ serializer for listing Trending posts with data with Total Likes and Likes of Current week """
    likes = serializers.SerializerMethodField()
    latest_like = serializers.IntegerField(read_only=True)

    class Meta:
        model = Posts
        fields = ['id', 'title', 'overview', 'description', 'category_id', 'posted_by', 'likes', 'latest_like']
        extra_kwargs = {
            'id': {'read_only': True},
            'posted_by': {'read_only': True}
        }

    """ getting Total Likes On Post using SerializerMethod"""
    @staticmethod
    def get_likes(self, obj):
        return obj.post_like.filter().count()
