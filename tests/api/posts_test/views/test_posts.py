import pytest
from posts.models import Posts, Likes, Comments


@pytest.mark.django_db
def test_create_post_fail(client, auth_user_client):
    payload = {
        "title": ""
    }
    response = client.post('/api/user/post/create_posts/', payload)
    data = response.data
    assert response.status_code == 400
    assert data['title'][0] == "This field may not be blank."


@pytest.mark.django_db
def test_create_post_success(client, auth_user_client):
    payload = {
        "title":"first post"
    }
    response = client.post("/api/user/post/create_posts/", payload)
    assert response.status_code == 200


@pytest.mark.django_db
def test_list_posts_fail(client, auth_user_client, user):
    user_id = user.id
    response = auth_user_client.get(f"/api/user/post/post-list/{user_id}/")
    assert response.status_code == 400


@pytest.mark.django_db
def test_list_posts_success(client, auth_user_client, user):
    user_id = user.id
    post_payload = {
        "title": "hi",
        "posted_by": user
    }
    Posts.objects.create(**post_payload)
    response = auth_user_client.get(f"/api/user/post/post-list/{user_id}/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_posts_fail(client, auth_user_client, user):
    post_payload = {
        "title": "hi",
        "posted_by": user
    }
    post = Posts.objects.create(**post_payload)
    post_payload = {
        "post_id": 0,
        "title": "hello"
    }
    response = auth_user_client.patch(f"/api/user/post/manage-post/", post_payload)
    data = response.data
    assert response.status_code == 404


@pytest.mark.django_db
def test_update_posts_success(client, auth_user_client, user):
    user_id = user.id
    post_payload = {
        "title": "hi",
        "posted_by": user
    }
    post = Posts.objects.create(**post_payload)
    post_payload = {
        "post_id": post.id,
        "title": "hello"
    }
    response = auth_user_client.patch(f"/api/user/post/manage-post/", post_payload)
    data = response.data
    assert response.status_code == 200


@pytest.mark.django_db
def test_delete_posts_fail(client, auth_user_client, user):
    post_payload = {
        "title": "hi",
        "posted_by": user
    }
    Posts.objects.create(**post_payload)
    post_payload = {
        "title": "hello"
    }
    response = auth_user_client.patch(f"/api/user/post/manage-post/", post_payload)
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_posts_success(client, auth_user_client, user):
    post_payload = {
        "title": "hi",
        "posted_by": user
    }
    post = Posts.objects.create(**post_payload)
    post_payload = {
        "post_id": post.id,
        "title": "hello"
    }
    response = auth_user_client.delete(f"/api/user/post/manage-post/", post_payload)
    assert response.status_code == 204


@pytest.mark.django_db
def test_upload_file_fail(client, auth_user_client, user):
    post_payload = {
        "title": "hi",
        "posted_by": user
    }
    post = Posts.objects.create(**post_payload)
    with open('media/posts/2.jpeg', 'rb') as image_file:
        payload = {
                "post_id": post.id
            }
        response = client.post("/api/user/post/upload_file/", payload)
    data = response.data
    assert response.status_code == 400
    assert data['file'][0] == 'No file was submitted.'


@pytest.mark.django_db
def test_upload_file_success(client, auth_user_client, user):
    post_payload = {
        "title": "hi",
        "posted_by": user
    }
    post = Posts.objects.create(**post_payload)
    with open('media/posts/2.jpeg', 'rb') as image_file:
        payload = {
                "post_id": post.id,
                "file": image_file
            }
        response = client.post("/api/user/post/upload_file/", payload)
    data = response.data
    assert response.status_code == 200
    assert data['msg'] == 'File Uploaded Successfully'


@pytest.mark.django_db
def test_list_posts_by_friend_fail(client, auth_user_client, user,
                                   second_user, create_post_by_second_user):
    response = auth_user_client.get(f"/api/user/post/post-list/{second_user.id}/")
    data = response.data
    assert response.status_code == 400
    assert data['Error'] == 'Only Friends Can See all Posts'


@pytest.mark.django_db
def test_list_posts_by_friend_success(client, auth_user_client, user, second_user,
                                      friends, create_post_by_second_user):

    response = auth_user_client.get(f"/api/user/post/post-list/{second_user.id}/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_like_post_fail(client, auth_user_client, friends, user,
                        second_user, create_post_by_second_user):
    response = auth_user_client.post(f"/api/user/post/like-post/")
    data = response.data
    assert response.status_code == 406
    assert data["Error"] == " 'post_id' is Required to Like Post"


@pytest.mark.django_db
def test_like_post_success(client, auth_user_client, friends, user,
                           second_user, create_post_by_second_user):
    payload = {
        "post_id": create_post_by_second_user.id
    }
    response = auth_user_client.post(f"/api/user/post/like-post/", payload)
    data = response.data
    assert response.status_code == 200
    assert data['message'] == 'you liked a post'


@pytest.mark.django_db
def test_remove_like_on_post_fail(client, auth_user_client, user, create_post_by_second_user):

    payload = {
        "post_id": create_post_by_second_user.id,
    }
    response = auth_user_client.delete(f"/api/user/post/remove-like-on-post/", payload)
    data = response.data
    assert response.status_code == 400
    assert data["msg"] == "'post_id and 'id' are Required Field For Delete Like Data "


@pytest.mark.django_db
def test_remove_like_on_post_success(client, auth_user_client, friends, user,
                                     create_post_by_second_user):
    like = Likes.objects.create(liked_by_id=user.id,
                                post_id_id=create_post_by_second_user.id)
    payload = {
        "post_id": create_post_by_second_user.id,
        "id": like.id
    }
    response = auth_user_client.delete(f"/api/user/post/remove-like-on-post/", payload)
    data = response.data
    assert response.status_code == 204
    assert data['message'] == 'Like Removed SuccessFully'


@pytest.mark.django_db
def test_comment_on_post_fail_for_friend(client, user, auth_user_client, create_post_by_second_user):
    payload = {
        "post_id": create_post_by_second_user.id
    }
    response = auth_user_client.post(f"/api/user/post/comment-on-post/", payload)
    data = response.data
    assert response.status_code == 400
    assert data['msg'] == 'Only Friends Can Comment on This Post'


@pytest.mark.django_db
def test_comment_on_post_fail_for_post_id(client, user, auth_user_client, create_post_by_second_user):
    response = auth_user_client.post(f"/api/user/post/comment-on-post/",)
    data = response.data
    assert response.status_code == 406
    assert data['msg'] == " 'post_id' is Required to Make Comment On a Post"


@pytest.mark.django_db
def test_comment_on_post_success(client, user, auth_user_client, friends,
                                 create_post_by_second_user):
    payload = {
        "post_id": create_post_by_second_user.id,
        "comment": "test Comment"
    }
    response = auth_user_client.post(f"/api/user/post/comment-on-post/", payload)
    data = response.data
    assert response.status_code == 200
    assert data['message'] == 'you commented on a post'


@pytest.mark.django_db
def test_delete_comment_on_post_fail_for_comment_id(client, user, auth_user_client, friends,
                                                    create_post_by_second_user):
    comment_payload = {
        "post_id": create_post_by_second_user.id,
        "comment": "test Comment"
    }
    response = auth_user_client.post(f"/api/user/post/comment-on-post/", comment_payload)
    payload = {
        "post_id": create_post_by_second_user.id
    }
    response = auth_user_client.delete(f"/api/user/post/delete-comment-on-post/")
    data = response.data
    assert response.status_code == 400
    assert data['msg'] == "'post_id and 'id' are Required Field For Delete Comment Data "


@pytest.mark.django_db
def test_delete_comment_on_post_success(client, user, auth_user_client, friends,
                                        create_post_by_second_user):
    comment_payload = {
        "post_id": create_post_by_second_user.id,
        "comment": "test Comment"
    }
    response = auth_user_client.post(f"/api/user/post/comment-on-post/", comment_payload)
    data = response.data
    comment_id = data['data']['id']
    payload = {
        "post_id": create_post_by_second_user.id,
        "id": comment_id
    }
    response = auth_user_client.delete(f"/api/user/post/delete-comment-on-post/", payload)
    data = response.data
    assert response.status_code == 204
    assert data['message'] == 'Comment Deleted SuccessFully'


@pytest.mark.django_db
def test_trending_feature_fail(client, second_user,):
    for i in range(3):
        create_post_payload = {
            "title": f"test_post_{i}",
            "posted_by": second_user,
            "is_public": True
        }
        Posts.objects.create(**create_post_payload)

    response = client.get("/api/user/post/trending-posts/")
    data = response.data
    assert response.status_code == 401
    assert data['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_trending_feature_success(auth_user_client, second_user,):
    for i in range(3):
        create_post_payload = {
            "title": f"test_post_{i}",
            "posted_by": second_user,
            "is_public": True
        }
        Posts.objects.create(**create_post_payload)

    response = auth_user_client.get("/api/user/post/trending-posts/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_comment_on_post_fail_for_comment_id(client, user, auth_user_client, friends,
                                                 create_post_by_second_user):
    comment_payload = {
        "post_id": create_post_by_second_user.id,
        "comment": "test Comment"
    }
    response = auth_user_client.post(f"/api/user/post/comment-on-post/", comment_payload)
    response = auth_user_client.post(f"/api/user/post/delete-comment-on-post/")
    data = response.data
    assert response.status_code == 400
    assert data['msg'] == "'post_id and 'id' are Required Field For Get Comment Data "


@pytest.mark.django_db
def test_get_comment_on_post_success(client, user, auth_user_client, friends,
                                     create_post_by_second_user):
    comment_payload = {
        "post_id": create_post_by_second_user.id,
        "comment": "test Comment"
    }
    response = auth_user_client.post(f"/api/user/post/comment-on-post/", comment_payload)
    data = response.data
    comment_id = data['data']['id']
    payload = {
        "post_id": create_post_by_second_user.id,
        "id": comment_id
    }
    response = auth_user_client.post("/api/user/post/delete-comment-on-post/", payload)
    data = response.data
    assert response.status_code == 200
