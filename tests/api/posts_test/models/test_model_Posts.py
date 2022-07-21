import pytest
from posts.models import (PostCategories, Posts, UploadedFiles, Likes, Comments)
from django.core.files import File


@pytest.mark.django_db
def test_create_PostCategory_model(client):
    post_category = PostCategories.objects.create(category="General")
    assert post_category.category == "General"


@pytest.mark.django_db
def test_update_PostCategory_model(client):
    post_category = PostCategories.objects.create(category="General")
    post_category.category = "Food"
    assert post_category.category == "Food"


@pytest.mark.django_db
def test_delete_PostCategory_model(client):
    post_category = PostCategories.objects.create(category="General")
    PostCategories.objects.get(id=post_category.id).delete()
    assert PostCategories.objects.all().count() == 0


@pytest.mark.django_db
def test_create_Post_model(client, user, second_user):
    post = Posts.objects.create(posted_by=user,
                                title="test post")
    assert post.posted_by == user


@pytest.mark.django_db
def test_update_Post_model(client, user, second_user):
    post = Posts.objects.create(posted_by=user,
                                title="test post")
    post.title = "updated post"
    post.save()
    assert post.title == "updated post"


@pytest.mark.django_db
def test_delete_Post_model(client, user, second_user):
    post = Posts.objects.create(posted_by=user,
                                title="test post")
    Posts.objects.get(id=post.id).delete()
    assert Posts.objects.all().count() == 0


@pytest.mark.django_db
def test_Likes_model(client, user, create_post, second_user):
    like = Likes.objects.create(post_id=create_post,
                                liked_by=user)
    assert like.liked_by == user


@pytest.mark.django_db
def test_delete_Likes_model(client, user, create_post, second_user):
    like = Likes.objects.create(post_id=create_post,
                                liked_by=user)

    Likes.objects.get(id=like.id).delete()
    assert Likes.objects.all().count() == 0


@pytest.mark.django_db
def test_comment_model(client, user, create_post, second_user):
    comment = Comments.objects.create(post_id=create_post,
                                      commented_by=user,
                                      comment="hello")
    assert comment.commented_by == user
    assert comment.post_id == create_post
    assert comment.comment == "hello"


@pytest.mark.django_db
def test_delete_comment_model(client, user, create_post, second_user):
    comment = Comments.objects.create(post_id=create_post,
                                      commented_by=user,
                                      comment="hello")

    Comments.objects.get(id=comment.id).delete()
    assert Comments.objects.all().count() == 0


@pytest.mark.django_db
def test_upload_file(client, user, create_post):
    image_file = open('media/posts/1.jpg', 'rb')
    file_obj = File(image_file)

    payload = {
            "post_id": create_post,
            "file": file_obj
        }
    upload_file = UploadedFiles.objects.create(**payload)
    assert upload_file.post_id == create_post
    # assert upload_file.file == file_obj
    # Here Cloudinary adds some extra unique name for file So we can not check same file name
