from django.shortcuts import get_object_or_404
# from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Posts, UploadedFiles
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import User, Likes, Comments
from Friends.utils import check_is_friend
from authentication.permissions import IsOwner
from .serializers import (PostSerializer, UploadFilesSerializer, PostModelSerializer, UpdateDeleteFilesSerializer,
                          UpdateDeletePostSerializer, LikePostSerializer, CommentOnPostSerializer,
                          TrendingFeedsSerializer)
import datetime as DT


class PostCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """ 
    Create Posts API view first authenticate the User and then it will allow to create POSTS for that User
    In this View User Can Only post text Data
    """

    def post(self, request, format=None):
        """ getting user_id of Authenticated User to Create Post """
        posted_by = request.user.id
        request.data['posted_by'] = posted_by

        """ passing user_id as posted_by using PostModelSerializer and then check for Valid Serializer"""
        serializer = PostModelSerializer(data=request.data, context={'posted_by': posted_by})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'data': serializer.data, 'msg': 'Post Created Successfully'},
                        status=status.HTTP_200_OK)


class UploadFileAPIView(APIView):
    """
    After Authentication and After Creating Post this View will Allow User to Upload files into that Blog
    In this View User Can Only post file Data
    """

    def post(self, request, format=None):
        """ getting user_id of Authenticated User to Create Post """
        """ serializing File data and check if that is valid or not """
        serializer = UploadFilesSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'data': serializer.data, 'msg': 'File Uploaded Successfully'},
                        status=status.HTTP_200_OK)


class PostLists(generics.ListAPIView):
    """
    Listing Post through this APIView after Authenticating that user it will list out
    all post for provided user_id
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    pagination_class = PageNumberPagination

    """ getting all Objects of the post through get_queryset """
    def get_queryset(self):
        posted_by = self.request.data.get('posted_by')
        queryset = Posts.objects.filter(posted_by=posted_by)
        return queryset

    """ getting all data of Post from posts and uploaded File through posted_by id """
    def get(self, request, *args, **kwargs):
        posted_by = self.request.data.get('posted_by')
        user_id = request.user.id
        if posted_by is None or posted_by == "":
            return Response(
                {'msg': " 'posted_by' id not provide"},
                status=status.HTTP_400_BAD_REQUEST
                )
        """ checking Provided User_id is Valid or not"""
        if not User.objects.filter(id=posted_by).exists():
            return Response({
                'msg': 'User Not Exists'
            })
        friends = check_is_friend(user_id, posted_by)
        if str(user_id) != str(posted_by):
            if friends is None:
                return Response({'msg': f'only friends can see Posts'})
            else:
                if friends[0] is False:
                    return Response({'msg': f'only friends can see Posts'})
        queryset = self.get_queryset()

        """Adding Pagination and Creating Pages"""
        page = self.paginate_queryset(queryset)
        if page:
            serializer = PostSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = PostSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateDeletePosts(generics.RetrieveUpdateDestroyAPIView):
    """ Update and Delete Posts through this view"""
    queryset = Posts.objects.all()
    serializer_class = UpdateDeletePostSerializer
    """ checking permission for authentication and IsOwner or Not """
    permission_classes = [IsOwner, IsAuthenticated]

    def get_object(self):
        """ getting post-id and creating Obj of user for checking condition IsOwner or not"""
        queryset = self.get_queryset()
        post_id = self.request.data.get('post_id')
        obj = get_object_or_404(queryset, id=post_id)
        """ after creating Object check that permission is provided or not for that user Object"""
        self.check_object_permissions(self.request, obj.posted_by)
        return obj

    def patch(self, request, *args, **kwargs):
        """
         getting Response when User Update Post (text data) like
         title, overview, description etc
        """
        response = super(UpdateDeletePosts, self).partial_update(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Posts updated successfully."},
            status=response.status_code
        )

    def delete(self, request, *args, **kwargs):
        """ deleting user post it will also delete post files """
        response = super(UpdateDeletePosts, self).destroy(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Posts deleted successfully."},
            status=response.status_code
        )


class UpdateDeleteFiles(generics.RetrieveUpdateDestroyAPIView):
    """ Update and delete Post file """
    serializer_class = UpdateDeleteFilesSerializer
    """ checking permissions like IsAuthenticated and IsOwner or  Not """
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        """ taking File_id to Update or Delete that file"""
        file_id = self.request.data.get('file_id')
        queryset = UploadedFiles.objects.filter(id=file_id)
        """ creating object to get data of provided file_id"""
        obj = get_object_or_404(queryset, id=file_id)
        """
        creating another object from first object to check that user 
        is owner of that file or not
        """
        obj1 = obj.post_id.posted_by
        """ checking user permissions """
        self.check_object_permissions(self.request, obj1)
        return obj

    def patch(self, request, *args, **kwargs):
        """ partially updating File Data """
        response = super(UpdateDeleteFiles, self).partial_update(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Posts updated successfully."},
            status=response.status_code
        )

    def delete(self, request, *args, **kwargs):
        """deleting file object of provide file_id"""
        response = super(UpdateDeleteFiles, self).destroy(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Posts deleted successfully."},
            status=response.status_code
        )


class SinglePostListView(generics.ListAPIView):
    """
    Listing Post through this APIView after Authenticating that user it will list out
    post data by provided post_id
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    """ getting all Objects of the post through get_queryset """
    def get_queryset(self):

        post_id = self.request.data.get('post_id')
        queryset = Posts.objects.filter(id=post_id)
        return queryset

    """ getting all data of Post from posts and uploaded File through post_id """
    def get(self, request, *args, **kwargs):
        post_id = self.request.data.get('post_id')

        """if post_id is not Provided then this will show message """
        if post_id is None or post_id == "":
            return Response(
                {'msg': 'post id not provide'},
                status=status.HTTP_400_BAD_REQUEST
                )
        """ checking Provided post_id is Valid or not"""
        queryset1 = Posts.objects.filter(id=post_id).first()
        if queryset1 is None:
            return Response({
                'msg': 'Post Not Found'
            })
        """ if valid post_id is Provided and if data is available then it will return that data  """
        response = super(SinglePostListView, self).get(request, *args, **kwargs)
        return Response(
                response.data,
                status=response.status_code
            )


class LikePostView(generics.CreateAPIView):
    """ Creating an Endpoint for Like Posts authenticated User Can Like Posts Of Friend or Own Post"""
    serializer_class = LikePostSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """ Overriding create method to create custom request for Like Post endpoint """
        liked_by = request.user.id
        """Getting Data with data fields (mainly Post_id) from users to Like the post of given Post id"""
        data = request.data
        if 'post_id' not in data.keys():
            return Response({"msg": " 'post_id' is Required to Like Post"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        post_id = data['post_id']
        data['liked_by'] = liked_by
        """ Checking that Post owner and user is friends or not """
        obj = Posts.objects.get(id=post_id)
        post_owner = obj.posted_by.id
        friend_status = None
        if str(liked_by) != str(post_owner):
            friend_status = check_is_friend(liked_by, post_owner)
        if friend_status is not None and friend_status[0] is True or str(liked_by) == str(post_owner):
            """ check that User has Liked this Post Before or Not If user liked this post than new like
             should not be considered """
            queryset1 = Likes.objects.filter(liked_by=liked_by, post_id=post_id).first()
            if queryset1 is not None:
                return Response({"msg": "You have Already Liked this Post"})
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 200,
                    'message': 'you liked a post',
                    'data': serializer.data
                })
        else:
            return Response({'msg': 'Only Friends Can Like This Post'})

        return Response({
            'data': serializer.errors, 'msg': 'Some error has occurred'}, status=status.HTTP_400_BAD_REQUEST
        )


class CommentOnPostView(generics.CreateAPIView):
    """ Overriding create method to create custom request for Like Post endpoint """
    serializer_class = CommentOnPostSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        commented_by = request.user.id
        """Getting Data with data fields (mainly Post_id) from users to Comment on the post of given Post id"""
        data = request.data
        if 'post_id' not in data.keys():
            return Response({"msg": " 'post_id' is Required to Make Comment On a Post"},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        post_id = data['post_id']
        data['commented_by'] = commented_by
        obj = Posts.objects.get(id=post_id)
        post_owner = obj.posted_by.id
        """ Checking Friend Status of User And Post Owner """
        friend_status = None

        if str(commented_by) != str(post_owner):
            friend_status = check_is_friend(commented_by, post_owner)
        if friend_status is not None and friend_status[0] is True or str(commented_by) == str(post_owner):
            """ If User is a friend Of Post_owner who have uploaded post only then he/she should be able to 
            comment on that Post """
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 200,
                    'message': 'you commented on a post',
                    'data': serializer.data
                })
        else:
            return Response({'msg': 'Only Friends Can Comment on This Post'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'data': serializer.errors, 'msg': 'Some error has occurred'}, status=status.HTTP_400_BAD_REQUEST
        )


class RetrieveDestroyCommentAPIView(generics.RetrieveDestroyAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """
    serializer_class = CommentOnPostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        data = self.request.data
        if 'post_id' and 'id' in data.keys():
            comment_id = data.get('id')
            post_id = data.get('post_id')
            queryset = Comments.objects.filter(id=comment_id, post_id=post_id)
            return queryset
        else:
            None

    def get_object(self):
        """ getting query_set and creating Obj of user for  managing Comments """
        queryset = self.get_queryset()
        if queryset is None:
            return None
        obj = get_object_or_404(queryset)
        return obj

    def get(self, request, *args, **kwargs):
        obj1 = self.get_object()
        data = self.request.data
        if 'post_id' and 'id' not in data.keys():
            return Response({"msg": "'post_id and 'id' are Required Field For Get Comment Data "},
                            status=status.HTTP_400_BAD_REQUEST)
        if obj1 is None:
            return Response({"msg": "No Comments yet"})
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """deleting comment object of provide post_id and id """
        obj1 = self.get_object()
        data = self.request.data
        if 'post_id' and 'id' not in data.keys():
            return Response({"msg": "'post_id and 'id' are Required Field For Delete Comment Data "},
                            status=status.HTTP_400_BAD_REQUEST)
        if obj1 is None:
            return Response({"msg": "No Comments yet"}, status=status.HTTP_400_BAD_REQUEST)
        response = super(RetrieveDestroyCommentAPIView, self).destroy(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Comment Deleted SuccessFully"},
            status=response.status_code
        )


class RetrieveDestroyLikeAPIView(generics.RetrieveDestroyAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """
    serializer_class = LikePostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        data = self.request.data
        if 'post_id' and 'id' in data.keys():
            like_id = data.get('id')
            post_id = data.get('post_id')
            queryset = Likes.objects.filter(id=like_id, post_id=post_id)
            return queryset
        else:
            None

    def get_object(self):
        """ getting query_set and creating Obj of user for  managing likes On Post"""
        queryset = self.get_queryset()
        if queryset is None:
            return None
        obj = get_object_or_404(queryset)
        return obj

    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        obj1 = self.get_object()
        data = self.request.data
        if 'post_id' and 'id' not in data.keys():
            return Response({"msg": "'post_id and 'id' are Required Field For Get Like Data "},
                            status=status.HTTP_400_BAD_REQUEST)
        if obj1 is None:
            return Response({"msg": "No Likes yet"}, status=status.HTTP_400_BAD_REQUEST)
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """deleting like object of provide like_id and id"""
        obj1 = self.get_object()
        data = self.request.data
        if 'post_id' and 'id' not in data.keys():
            return Response({"msg": "'post_id and 'id' are Required Field For Delete Like Data "},
                            status=status.HTTP_400_BAD_REQUEST)
        if obj1 is None:
            return Response({"msg": "No Likes yet"}, status=status.HTTP_400_BAD_REQUEST)
        response = super(RetrieveDestroyLikeAPIView, self).destroy(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Like Removed SuccessFully"},
            status=response.status_code
        )


class TrendingFeedAPIView(generics.ListAPIView):
    """ Trending Posts will be Listing Through This APIView by The use Of TrendingFeedsSerializer"""
    permission_classes = [IsAuthenticated]
    serializer_class = TrendingFeedsSerializer

    def get_queryset(self):
        """getting Latest Trending Posts Through data of Today and """
        today = DT.date.today()
        week_ago = today - DT.timedelta(days=7)
        queryset = Posts.objects.filter(is_public=True).annotate(
            latest_like=Count('post_like', filter=Q(post_like__created_at__gte=week_ago))
        ).order_by("-latest_like")[:10]
        return queryset






