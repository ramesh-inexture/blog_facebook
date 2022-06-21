from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Posts, UploadedFiles
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import User
from authentication.permissions import IsOwner
from .serializers import (PostSerializer, UploadFilesSerializer, PostModelSerializer, UpdateDeleteFilesSerializer,
                          UpdateDeletePostSerializer)


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
        post_id = request.data.get('post_id')
        request.data['post_id'] = post_id
        """ serializing File data and check if that is valid or not """
        serializer = UploadFilesSerializer(data=request.data, context={'post_id': post_id})
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
    queryset = Posts.objects.all()

    """ getting all Objects of the post through get_queryset """
    def get_queryset(self):
        posted_by = self.request.data.get('posted_by')
        queryset = Posts.objects.filter(posted_by=posted_by)
        return queryset

    """ getting all data of Post from posts and uploaded File through posted_by id """
    def get(self, request, *args, **kwargs):
        posted_by = self.request.data.get('posted_by')

        """if Posted_by (user_id) is not Provided then this will show message """
        if posted_by is None or posted_by == "":
            return Response(
                {'msg':'posted_by id not provide'},
                status=status.HTTP_400_BAD_REQUEST
                )
        """ checking Provided User_id is Valid or not"""
        queryset1 = User.objects.filter(id=posted_by).first()
        if queryset1 is None:
            return Response({
                'msg':'User Not Found'
            })
        """ if valid Posted_by (user_id) is Provided and if data is available then it will return that data """
        response = super(PostLists, self).get(request, *args, **kwargs)
        return Response(
                response.data,
                status=response.status_code
            )


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


# class SinglePostListView(generics.ListAPIView):
#     serializer_class = PostSerializer
#
#     def get_queryset(self):
#         post_id = self.request.data.get('post_id')
#         queryset = UploadedFiles.objects.filter(post_id=post_id)
#         return queryset

class SinglePostListView(generics.ListAPIView):
    """
    Listing Post through this APIView after Authenticating that user it will list out
    post data by provided post_id
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    # queryset = Posts.objects.all()

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





# /api/update/?pk=3
#
# /api/update/
#
# def self, request, *args, **kwargs
#     self.request.GET.data('pk')