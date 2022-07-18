import pytest
from django.urls import reverse

from posts.models import Posts


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
    data = response.data
    assert response.status_code == 200


@pytest.mark.django_db
def test_list_posts_fail(client, auth_user_client, user):
    user_id = user.id
    response = auth_user_client.get(f"/api/user/post/post-list/{user_id}/")
    data = response.data
    assert response.status_code == 400


@pytest.mark.django_db
def test_list_posts_success(client, auth_user_client, user):
    user_id = user.id
    post_payload = {
        "title":"hi",
        "posted_by": user
    }
    post = Posts.objects.create(**post_payload)
    response = auth_user_client.get(f"/api/user/post/post-list/{user_id}/")
    data = response.data
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_posts_fail(client, auth_user_client, user):
    user_id = user.id
    post_payload = {
        "title": "hi",
        "posted_by": user
    }
    post = Posts.objects.create(**post_payload)
    post_payload = {
        "post_id": 5,
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
    user_id = user.id
    post_payload = {
        "title": "hi",
        "posted_by": user
    }
    post = Posts.objects.create(**post_payload)
    post_payload = {
        "title": "hello"
    }
    response = auth_user_client.patch(f"/api/user/post/manage-post/", post_payload)
    data = response.data
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_posts_success(client, auth_user_client, user):
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
    response = auth_user_client.delete(f"/api/user/post/manage-post/", post_payload)
    data = response.data
    assert response.status_code == 204


@pytest.mark.django_db
def test_upload_file_fail(client, auth_user_client, user):
    user_id = user.id
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
    user_id = user.id
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
