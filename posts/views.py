from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import generics, status
from blog.constants import LIKE_HEADER,LIKE_BODY, COMMENT_HEADER, COMMENT_BODY
from authentication.models import RestrictedUsers
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import User, Likes, Comments, Posts, UploadedFiles
from Friends.utils import check_is_friend
from notifications.utils import send_notification
from authentication.permissions import IsOwner, IsOwnerOrIsAdmin, IsUserActive
from .serializers import (PostSerializer, UploadFilesSerializer, PostModelSerializer, UpdateDeleteFilesSerializer,
                          UpdateDeletePostSerializer, LikePostSerializer, CommentOnPostSerializer,
                          TrendingFeedsSerializer)
import datetime as DT


class PostCreateAPIView(APIView):
    """ 
    Create Posts API view first authenticate the User and then it will allow to create POSTS for that User
    In this View User Can Only post text Data
    """
    permission_classes = [IsAuthenticated, IsUserActive]

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
    permission_classes = [IsAuthenticated, IsOwner]

    def post(self, request, format=None):
        """ getting user_id of Authenticated User to Create Post
         serializing File data and check if that is valid or not """
        data=request.data
        if 'post_id' in data:
            id = data['post_id']
            Post_obj = get_object_or_404(Posts, id=id)
            self.check_object_permissions(self.request, Post_obj.posted_by)
        serializer = UploadFilesSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            """ here if Serializer is Valid then it Will be saved by serializer.save  else 
            it will raise exception from above given argument 'raise_exception=true' """
            serializer.save()
        return Response({'data': serializer.data, 'msg': 'File Uploaded Successfully'},
                        status=status.HTTP_200_OK)


class PostLists(generics.ListAPIView):
    """
    Listing Post through this APIView after Authenticating that user it will list out
    all post for provided user_id
    """
    permission_classes = [IsAuthenticated, IsUserActive]
    serializer_class = PostSerializer
    pagination_class = PageNumberPagination

    """ getting all Objects of the post through get_queryset """
    def get_queryset(self, pk):
        queryset = Posts.objects.filter(posted_by=pk)
        return queryset

    """ getting all data of Post from posts and uploaded File through posted_by id """
    def get(self, request, pk, *args, **kwargs):
        posted_by = pk
        user_id = request.user.id
        """ checking Provided User_id is Valid or not"""
        if not User.objects.filter(id=posted_by).exists():
            return Response({
                'msg': 'User Not Exists'
            })
        post_queryset = self.get_queryset(pk)
        if not post_queryset:
            raise ValidationError({"Error": "No Data Found"})
        post_owner = posted_by
        user = request.user.id
        is_post_owner_active = User.objects.get(id=posted_by).is_active
        blocked_by_post_owner = RestrictedUsers.objects.filter(blocked_by=post_owner, blocked_user=user)
        """ If Post owner is active and the User is Not Blocked By Post Owner then we Check that both Users
         are Friends or not if Both are Not Friends Then user can only see the Post owner's Public Posts"""
        if is_post_owner_active and not blocked_by_post_owner:
            if user_id != post_owner:
                is_friends = check_is_friend(post_owner, user)
                if not is_friends or not is_friends[0]:
                    public_posts = post_queryset.filter(is_public=True)
                    if public_posts:
                        post_queryset = public_posts
                    else:
                        raise ValidationError({"Error": "Only Friends Can See all Posts"})

            """Adding Pagination and Creating Pages"""
            page = self.paginate_queryset(post_queryset)
            if page:
                serializer = PostSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            else:
                serializer = PostSerializer(post_queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            raise ValidationError({"Error": "Post Owner is Not Active Or Post Owner Blocked You"})


class UpdateDeletePosts(generics.RetrieveUpdateDestroyAPIView):
    """ Update and Delete Posts through this view"""
    queryset = Posts.objects.all()
    serializer_class = UpdateDeletePostSerializer
    """ checking permission for authentication and IsOwner or Not """
    permission_classes = [IsAuthenticated, IsOwnerOrIsAdmin, IsUserActive]

    def get_object(self):
        """ getting post-id and creating Obj of user for checking condition IsOwner or not"""
        post_id = self.request.data.get('post_id')
        queryset = self.get_queryset()
        post_obj = get_object_or_404(queryset, id=post_id)
        """ after creating Object check that permission is provided or not for that user Object"""
        self.check_object_permissions(self.request, post_obj.posted_by)
        return post_obj

    def patch(self, request, *args, **kwargs):
        """ Getting Response when User Update Post (text data) like title, overview, description etc """
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
    permission_classes = [IsAuthenticated, IsOwner, IsUserActive]

    def get_object(self):
        """ taking File_id to Update or Delete that file"""
        file_id = self.request.data.get('file_id')
        queryset = UploadedFiles.objects.filter(id=file_id)
        """ creating object to get data of provided file_id"""
        file_obj = get_object_or_404(queryset, id=file_id)
        """
        creating another object from first object to check that user 
        is owner of that file or not
        """
        posted_by_obj = file_obj.post_id.posted_by
        """ checking user permissions """
        self.check_object_permissions(self.request, posted_by_obj)
        return file_obj

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


class SinglePostListView(generics.RetrieveAPIView):
    """
    Listing Post through this APIView after Authenticating that user it will list out
    post data by provided post_id
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    queryset = Posts.objects.all()

    def get(self, request, pk, *args, **kwargs):
        """ getting all data of Post from posts and uploaded File through post_id """
        post_id = pk
        """if post_id is not Provided then this will show message """
        if not post_id:
            return Response(
                {'post_id': 'Not provide'},
                status=status.HTTP_400_BAD_REQUEST
                )
        """ checking Provided post_id is Valid or not"""
        posts_obj = self.get_queryset()[0]
        if not posts_obj:
            return Response({
                'msg': 'Data Not Found'
            }, status=status.HTTP_404_NOT_FOUND)

        """Creating posts_obj to check active status of post owner and also checking if post is not public
         then they should have to be friend with user"""
        # posts_obj = get_object_or_404(post_queryset)
        # po
        post_owner = posts_obj.posted_by.id
        user = request.user.id
        is_post_owner_active = posts_obj.posted_by.is_active
        blocked_by_post_owner = RestrictedUsers.objects.filter(blocked_by=post_owner, blocked_user=user)
        if is_post_owner_active and not blocked_by_post_owner:
            is_friends = check_is_friend(post_owner,user)
            if not posts_obj.is_public:
                if post_owner != user:
                    if is_friends :
                        if not is_friends[0]:
                            raise ValidationError({"Error": "Only Friends Can See Posts"})
                    else:
                        raise ValidationError({"Error": "Only Friends Can See Posts"})

                """ if valid post_id is Provided and if data is available then it will return that data  """
                response = super(SinglePostListView, self).get(request, *args, **kwargs)
                return Response(
                        response.data,
                        status=response.status_code
                    )
        else:
            raise ValidationError({"Error": "Post Owner is Not Active Or Post Owner Blocked You"})


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

        """Creating posts_obj to check active status of post owner and also checking if post is not public
         then they should have to be friend with user"""
        post_obj = Posts.objects.get(id=post_id)
        post_owner = post_obj.posted_by.id
        post_owner_email = post_obj.posted_by.email
        is_blocked_by_post_owner = RestrictedUsers.objects.filter(blocked_by=post_owner, blocked_user=liked_by)
        if post_obj.posted_by.is_active and not is_blocked_by_post_owner:
            if str(liked_by) != str(post_owner) and not post_obj.is_public:
                friend_status = check_is_friend(liked_by, post_owner)
                if not friend_status or not friend_status[0]:
                    return Response({'msg': 'Only Friends Can Like This Post'})

            """ check that User has Liked this Post Before or Not If user liked this post than new like
                 should not be considered """
            user_name = request.user.user_name
            # liked_obj_queryset = Likes.objects.filter(liked_by=liked_by, post_id=post_id).first()
            # if liked_obj_queryset:
            #     return Response({"msg": "You have Already Liked this Post"})
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                """ Sending Notification through send_notification function Imported From notifications.utils"""
                serializer.save()
                recent_like_obj = Likes.objects.get(post_id=post_id,liked_by=liked_by)
                # print(recent_like_obj.created_at)
                liked_at_time = DT.datetime.strftime(recent_like_obj.created_at,"%Y-%m-%d %H:%M:%S")
                notification_data = {
                    'notified_user': post_owner,
                    'notified_by': liked_by,
                    'user_name': user_name,
                    'notification_receiver_email': post_owner_email,
                    'header_message': LIKE_HEADER,
                    'body_message': LIKE_BODY.format(user_name,post_obj.title,liked_at_time),
                    }
                is_send, data = send_notification(**notification_data)
                if not is_send:
                    return Response({'data': data, 'msg': 'Some error has occurred'}, status=status.HTTP_400_BAD_REQUEST)
                """ After Notification Created We will Going return Response of Serialized Data of Post Like """
                return Response({
                            'status': 200,
                            'message': 'you liked a post',
                            'data': serializer.data
                        })

            return Response({
                'data': serializer.errors, 'msg': 'Some error has occurred'}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            raise ValidationError({"Error": "Post Owner is Not Active Or Post Owner Blocked You"})


class CommentOnPostView(generics.CreateAPIView):
    """ Overriding create method to create custom request for Like Post endpoint """
    serializer_class = CommentOnPostSerializer
    permission_classes = [IsAuthenticated, IsUserActive]

    def create(self, request, *args, **kwargs):
        commented_by = request.user.id
        user_name = request.user.user_name
        """Getting Data with data fields (mainly Post_id) from users to Comment on the post of given Post id"""
        data = request.data
        if 'post_id' not in data.keys():
            return Response({"msg": " 'post_id' is Required to Make Comment On a Post"},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        post_id = data['post_id']
        data['commented_by'] = commented_by
        post_obj = Posts.objects.get(id=post_id)
        post_owner = post_obj.posted_by.id
        post_owner_email = post_obj.posted_by.email
        """ Checking Friend Status of User And Post Owner """
        friend_status = None
        is_blocked_by_post_owner = RestrictedUsers.objects.filter(blocked_by=post_owner, blocked_user=commented_by)

        if post_obj.posted_by.is_active and not is_blocked_by_post_owner:
            if str(commented_by) != str(post_owner) and not post_obj.is_public:
                friend_status = check_is_friend(commented_by, post_owner)
                if not friend_status or not friend_status[0]:
                    return Response({'msg': 'Only Friends Can Comment on This Post'}, status=status.HTTP_400_BAD_REQUEST)

            """ If User is a friend Of Post_owner who have uploaded post only then he/she should be able to 
            comment on that Post """
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                """ 
                Making an Serializer for notification For User
                To make Serializer We are Getting Serializer by importing NotificationSerializer from 
                notifications.serializers 
                """
                serializer.save()
                recent_comment_obj = Comments.objects.filter(post_id=post_id, commented_by=commented_by).first()
                commented_at_time = DT.datetime.strftime(recent_comment_obj.created_at,"%Y-%m-%d %H:%M:%S")
                notification_data = {
                        'notified_user': post_owner,
                        'notified_by': commented_by,
                        'user_name': user_name,
                        'notification_receiver_email': post_owner_email,
                        'header_message': COMMENT_HEADER,
                        'body_message': COMMENT_BODY.format(user_name,post_obj.title, commented_at_time,
                                                            data['comment']),
                }
                is_send, data = send_notification(**notification_data)

                if not is_send:
                    return Response({'data': data, 'msg': 'Some error has occurred'},
                                    status=status.HTTP_400_BAD_REQUEST)
                """ After Notification Created We will Going To Save Serialized Data of Post Comment """
                return Response({
                    'status': 200,
                    'message': 'you commented on a post',
                    'data': serializer.data
                })

        return Response({
            'data': serializer.errors, 'msg': 'Some error has occurred'}, status=status.HTTP_400_BAD_REQUEST
        )


class RetrieveDestroyCommentAPIView(generics.RetrieveDestroyAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """
    serializer_class = CommentOnPostSerializer
    permission_classes = [IsOwnerOrIsAdmin, IsAuthenticated, IsUserActive]

    def get_queryset(self):
        data = self.request.data
        if 'post_id' and 'id' in data.keys():
            comment_id = data.get('id')
            post_id = data.get('post_id')
            queryset = Comments.objects.filter(id=comment_id, post_id=post_id)
            return queryset

    def get_object(self):
        """ getting query_set and creating Obj of user for  managing Comments """
        user_id = self.request.user.id
        queryset = self.get_queryset()
        if not queryset:
            return None
        comment_obj = get_object_or_404(queryset)
        commented_by = comment_obj.commented_by.id
        if user_id != commented_by:
            self.check_object_permissions(self.request, comment_obj.post_id.posted_by)
        return comment_obj

    def get(self, request, *args, **kwargs):
        """ Overriding get method to check whether provided data is valid or not"""
        comment_obj = self.get_object()
        data = self.request.data
        if 'post_id' and 'id' not in data:
            return Response({"msg": "'post_id and 'id' are Required Field For Get Comment Data "},
                            status=status.HTTP_400_BAD_REQUEST)
        if not comment_obj:
            return Response({"msg": "No Comments Found for this Id"})
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """deleting comment object of provide post_id and id """
        comment_obj = self.get_object()
        data = self.request.data
        if 'post_id' and 'id' not in data:
            return Response({"msg": "'post_id and 'id' are Required Field For Delete Comment Data "},
                            status=status.HTTP_400_BAD_REQUEST)
        if not comment_obj:
            return Response({"msg": "No Comments Found for this id"}, status=status.HTTP_400_BAD_REQUEST)

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
        if 'post_id' and 'id' in data:
            like_id = data.get('id')
            post_id = data.get('post_id')
            queryset = Likes.objects.filter(id=like_id, post_id=post_id)
            return queryset
        else:
            return None

    def get_object(self):
        """ getting query_set and creating Obj of user for  managing likes On Post"""
        queryset = self.get_queryset()
        if not queryset:
            return None
        post_like_obj = get_object_or_404(queryset)
        return post_like_obj

    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        post_like_obj = self.get_object()
        data = self.request.data
        if 'post_id' and 'id' not in data:
            return Response({"msg": "'post_id and 'id' are Required Field For Get Like Data "},
                            status=status.HTTP_400_BAD_REQUEST)
        if not post_like_obj:
            return Response({"msg": "No Likes yet"}, status=status.HTTP_400_BAD_REQUEST)
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """deleting like object of provide like_id and id"""
        post_like_obj = self.get_object()
        data = self.request.data
        if 'post_id' and 'id' not in data:
            return Response({"msg": "'post_id and 'id' are Required Field For Delete Like Data "},
                            status=status.HTTP_400_BAD_REQUEST)
        if not post_like_obj:
            return Response({"msg": "No Likes yet"}, status=status.HTTP_400_BAD_REQUEST)
        response = super(RetrieveDestroyLikeAPIView, self).destroy(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Like Removed SuccessFully"},
            status=response.status_code
        )


class TrendingFeedAPIView(generics.ListAPIView):
    """ Trending Posts will be Listing Through This APIView by The use Of TrendingFeedsSerializer"""
    permission_classes = [IsAuthenticated, IsUserActive]
    serializer_class = TrendingFeedsSerializer

    def get_queryset(self):
        """getting Latest Trending Posts Through data of Today and """
        today = DT.date.today()
        week_ago = today - DT.timedelta(days=7)
        queryset = Posts.objects.filter(is_public=True).annotate(
            latest_like=Count('post_like', filter=Q(post_like__created_at__gte=week_ago))
        ).order_by("-latest_like")[:10]
        return queryset
