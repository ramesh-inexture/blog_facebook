from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Posts, UploadedFiles
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import User
from authentication.permissions import IsOwner
from .serializers import (PostSerializer, UploadFilesSerializer, PostModelSerializer, UpdateDeleteFilesSerializer, UpdateDeletePostSerializer)


class PostCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        posted_by = request.user.id
        request.data['posted_by'] = posted_by
        print(posted_by)
        serializer = PostModelSerializer(data=request.data, context={'posted_by': posted_by})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'data': serializer.data, 'msg': 'Post Created Successfully'},
                        status=status.HTTP_200_OK)


class UploadFileAPIView(APIView):

    def post(self, request, format=None):
        post_id = request.data.get('post_id')
        request.data['post_id'] = post_id
        serializer = UploadFilesSerializer(data=request.data, context={'post_id': post_id})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'data': serializer.data, 'msg': 'File Uploaded Successfully'},
                        status=status.HTTP_200_OK)


class PostLists(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    queryset = Posts.objects.all()

    def get_queryset(self):
        posted_by = self.request.data.get('posted_by')
        queryset = Posts.objects.filter(posted_by=posted_by)
        return queryset

    def get(self, request, *args, **kwargs):
        posted_by = self.request.data.get('posted_by')

        if posted_by is None or posted_by == "":
            return Response(
                {'msg':'posted_by id not provide'},
                status=status.HTTP_400_BAD_REQUEST
                )
        queryset1 = User.objects.filter(id=posted_by).first()
        if queryset1 is None:
            return Response({
                'msg':'User Not Found'
            })
        response = super(PostLists, self).get(request, *args, **kwargs)
        return Response(
                response.data,
                status=response.status_code
            )


class UpdateDeletePosts(generics.RetrieveUpdateDestroyAPIView):

    queryset = Posts.objects.all()
    serializer_class = UpdateDeletePostSerializer
    permission_classes = [IsOwner, IsAuthenticated]

    # lookup_field = 'pk'

    def get_object(self):
        queryset = self.get_queryset()
        post_id = self.request.data.get('post_id')
        obj = get_object_or_404(queryset, id=post_id)
        self.check_object_permissions(self.request, obj.posted_by)
        return obj

    def patch(self, request, *args, **kwargs):
        response = super(UpdateDeletePosts, self).partial_update(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Posts updated successfully."},
            status=response.status_code
        )

    def delete(self, request, *args, **kwargs):
        response = super(UpdateDeletePosts, self).destroy(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Posts deleted successfully."},
            status=response.status_code
        )


class UpdateDeleteFiles(generics.RetrieveUpdateDestroyAPIView):

    # queryset = UploadedFiles.objects.all()
    serializer_class = UpdateDeleteFilesSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        file_id = self.request.data.get('file_id')
        queryset = UploadedFiles.objects.filter(id=file_id)
        obj = get_object_or_404(queryset, id=file_id)
        obj1 = obj.post_id.posted_by
        self.check_object_permissions(self.request, obj1)
        return obj

    def patch(self, request, *args, **kwargs):
        response = super(UpdateDeleteFiles, self).partial_update(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Posts updated successfully."},
            status=response.status_code
        )

    def delete(self, request, *args, **kwargs):
        response = super(UpdateDeleteFiles, self).destroy(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Posts deleted successfully."},
            status=response.status_code
        )


# class UploadFileList(generics.ListAPIView):
#     serializer_class = UpdateDeleteFilesSerializer
#
#     def get_queryset(self):
#         post_id = self.request.data.get('post_id')
#         queryset = UploadedFiles.objects.filter(post_id=post_id)
#         return queryset




# /api/update/?pk=3
#
# /api/update/
#
# def self, request, *args, **kwargs
#     self.request.GET.data('pk')