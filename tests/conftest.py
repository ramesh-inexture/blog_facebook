import pytest
from authentication.models import User
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
                                    user_name="azam",
                                    password="Test@123",
                                    password2="Test@123"
                                    )
    return user


@pytest.fixture()
def second_client():
    client = APIClient()
    return client


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
    response = client.post("/api/user/login/", payload)
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['token']['access'])
    return client
