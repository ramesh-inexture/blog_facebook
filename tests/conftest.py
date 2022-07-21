import pytest
from authentication.models import User
from Friends.models import Friends
from posts.models import Posts
from rest_framework.test import APIClient


@pytest.fixture()
def user():
    user = User.objects.create_user(email="dummy@gmail.com",
                                    user_name="dummy1",
                                    password="Test@123",
                                    password2="Test@123"
                                    )
    return user


@pytest.fixture()
def client():
    client = APIClient()
    return client


@pytest.fixture()
def second_user():
    user = User.objects.create_user(email="azzu@gmail.com",
                                    user_name="azhar",
                                    password="Test@123",
                                    password2="Test@123"
                                    )
    return user


@pytest.fixture()
def superuser():
    user = User.objects.create_superuser(email="ramesh@gmail.com",
                                         password="Test@123",
                                         password2="Test@123"
                                         )
    return user


@pytest.fixture
def auth_superuser_client(superuser, client):
    payload = {
        "email": "ramesh@gmail.com",
        "password": "Test@123",
    }
    response = client.post("/api/user/login/", payload)
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['token']['access'])
    return client


@pytest.fixture
def auth_user_client(user, client):
    payload = {
        "email": "dummy@gmail.com",
        "password": "Test@123",
    }
    response = client.post("/api/user/login/", payload, format='json')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['token']['access'])
    return client


@pytest.fixture
def create_post_by_second_user(second_user):
    post = Posts.objects.create(posted_by=second_user,
                                title="other post",
                                overview="testing other post")
    return post


@pytest.fixture
def create_post(user):
    post = Posts.objects.create(posted_by=user,
                                title="my post",
                                overview="test my post")
    return post


@pytest.fixture
def friends(user, second_user):
    sender = user
    receiver = second_user
    friend = Friends.objects.create(sender_id=sender,
                                    receiver_id=receiver,
                                    is_friend=True)
    return friend


@pytest.fixture
def friend_request(user, second_user):
    sender = second_user
    receiver = user
    friend_request = Friends.objects.create(sender_id=sender,
                                            receiver_id=receiver)
    return friend_request
