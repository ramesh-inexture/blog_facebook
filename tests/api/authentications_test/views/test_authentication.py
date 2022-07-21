import pytest


@pytest.mark.django_db
def test_register_user_fail(client):
    payload = {
        "email": "dummy@gmail.com",
        "password": "test@123",
        "password2": "test@123",
    }
    response = client.post("/api/user/register/", payload)
    data = response.data
    assert response.status_code == 400
    assert data['password'][0] == "The password must contain at least 1 uppercase letter, A-Z."


@pytest.mark.django_db
def test_register_user_success(client):
    payload = {
        "email": "dummy@gmail.com",
        "first_name": "ramesh",
        "last_name": "singh",
        "user_name": "rama1",
        "password": "Test@123",
        "password2": "Test@123",
    }
    response = client.post("/api/user/register/", payload)
    data = response.data
    assert response.status_code == 201
    assert "Registration Success" == data["msg"]
    assert "access" in data["token"]
    assert "refresh" in data["token"]
    assert "password" not in data
    assert "password2" not in data


@pytest.mark.django_db
def test_user_login_fail(user, client):
    payload = {
        "email": "new.inexture@gmail.com",
        "password": "Hacking@321",
    }
    response = client.post("/api/user/login/", payload)
    assert response.status_code == 404


@pytest.mark.django_db
def test_user_login_success(user, client, auth_user_client):
    payload = {
        "email": "dummy@gmail.com",
        "password": "Test@123",
    }
    response = client.post("/api/user/login/", payload)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_profile(auth_user_client):
    response = auth_user_client.get("/api/user/profile/")
    data = response.data
    assert response.status_code == 200
    assert data["email"] == "dummy@gmail.com"
    assert data["first_name"] == ""
    assert data["last_name"] == ""


@pytest.mark.django_db
def test_update_profile_success(auth_user_client):
    payload = {
        "first_name": "ramesh",
        "last_name": "singh",
    }
    response = auth_user_client.patch("/api/user/profile/", payload)
    data = response.data["data"]
    assert response.status_code == 200
    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]


@pytest.mark.django_db
def test_update_profile_fail(auth_user_client):
    payload = {
        "email": "ram12gmail.com",
        "name": "ramesh",
        "last_name": "singh",
    }
    response = auth_user_client.patch("/api/user/profile/", payload)
    data = response.data
    assert response.status_code == 400
    assert data["email"][0] == "Enter a valid email address."


@pytest.mark.django_db
def test_delete_profile_fail(client):
    response = client.delete("/api/user/profile/")
    data = response.data
    assert response.status_code == 401
    assert data['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_delete_profile_success(auth_user_client):
    response = auth_user_client.delete("/api/user/profile/")
    data = response.data
    assert response.status_code == 204
    assert data['message'] == "Profile deleted successfully."


@pytest.mark.django_db
def test_restrict_unrestrict_user_by_admin_fail(superuser, auth_superuser_client, user):
    users_id = user.id
    payload = {
        "is_active": ""
    }
    response = auth_superuser_client.patch(f"/api/user/restrict-unrestrict-user/{users_id}/", payload)
    data = response.data
    assert response.status_code == 400
    assert data["is_active"][0] == "Must be a valid boolean."


@pytest.mark.django_db
def test_block_user_by_admin_success(superuser, auth_superuser_client, user):
    users_id = user.id
    payload = {
        "is_active": False
    }
    response = auth_superuser_client.patch(f"/api/user/restrict-unrestrict-user/{users_id}/", payload)
    data = response.data
    assert response.status_code == 200
    assert data["message"] == "User Blocked successfully."


@pytest.mark.django_db
def test_unblock_user_by_admin_success(superuser, auth_superuser_client, user):
    users_id = user.id
    payload = {
        "is_active": "True"
    }
    response = auth_superuser_client.patch(f"/api/user/restrict-unrestrict-user/{users_id}/", payload)
    data = response.data
    assert response.status_code == 200
    assert data["message"] == "User UnBlocked successfully."


@pytest.mark.django_db
def test_block_user_by_user_fail(auth_user_client, user):
    users_id = user.id
    payload = {
        "is_active": "False"
    }
    response = auth_user_client.post(f"/api/user/block-unblock-user/{users_id}/", payload)
    data = response.data
    assert response.status_code == 400
    assert data["Error"] == "User can Not Block Own Account"


@pytest.mark.django_db
def test_block_user_by_user_success(auth_user_client, second_user):
    users_id = second_user.id
    payload = {
        "is_active": "False"
    }
    response = auth_user_client.post(f"/api/user/block-unblock-user/{users_id}/", payload)
    data = response.data
    assert response.status_code == 200
    assert data["msg"] == "User Blocked successfully."
