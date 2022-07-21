import pytest


@pytest.mark.django_db
def test_create_friend_fail_for_same_user_id(client, user, auth_user_client):
    sender = user.id
    receiver = user.id
    payload = {
        "sender_id": sender,
        "receiver_id": receiver
    }
    response = client.post("/api/user/friends/make-friend-request/", payload)
    print(response)
    data = response.data
    print("data", data)
    assert response.status_code == 400
    assert data['msg'] == 'sender_id and receiver_id can not be same'


@pytest.mark.django_db
def test_create_friend_fail_for_friend(client, user, auth_user_client, friends, second_user):
    sender = user.id
    receiver = second_user.id
    payload = {
        "sender_id": sender,
        "receiver_id": receiver
    }
    response = client.post("/api/user/friends/make-friend-request/", payload)
    print(response)
    data = response.data
    print("data", data)
    assert response.status_code == 400
    assert data['msg'] == f'receiver_id {receiver} is Already a Friend'


@pytest.mark.django_db
def test_create_friend_success(client, user, auth_user_client, second_user):
    sender = user.id
    receiver = second_user.id
    payload = {
        "sender_id": sender,
        "receiver_id": receiver
    }
    response = client.post("/api/user/friends/make-friend-request/", payload)
    data = response.data
    assert response.status_code == 201
    assert data['message'] == 'Friend Request created'


@pytest.mark.django_db
def test_see_friend_request_fail(client, user, friend_request):
    response = client.get("/api/user/friends/see-friend-requests/")
    data = response.data
    assert response.status_code == 401
    assert data['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_see_friend_request_success(client, user, auth_user_client, friend_request):
    response = client.get("/api/user/friends/see-friend-requests/")
    data = response.data
    assert response.status_code == 200


@pytest.mark.django_db
def test_accept_friend_request_fail(client, user, auth_user_client, friend_request, second_user):
    payload = {
        "sender_id": second_user.id,
        "is_friend": False
    }
    response = client.patch("/api/user/friends/manage-friend-request/", payload)
    data = response.data
    assert response.status_code == 400
    assert data['msg'] == "Update 'is_friend' to True to Accept Request"


@pytest.mark.django_db
def test_accept_friend_request_success(client, user, auth_user_client, friend_request, second_user):
    payload = {
        "sender_id": second_user.id,
        "is_friend": True
    }
    response = client.patch("/api/user/friends/manage-friend-request/", payload)
    data = response.data
    assert response.status_code == 200


@pytest.mark.django_db
def test_reject_friend_request_fail(client, user, second_user, auth_user_client, friend_request):
    payload = {
        "sender_id": 6
    }
    response = client.delete("/api/user/friends/manage-friend-request/", payload)
    data = response.data
    assert response.status_code == 404
    assert data["Details"] == "Data Not Found"


@pytest.mark.django_db
def test_reject_friend_request_success(client, user, second_user, auth_user_client, friend_request):
    payload = {
        "sender_id": second_user.id
    }
    response = client.delete("/api/user/friends/manage-friend-request/", payload)
    data = response.data
    assert response.status_code == 204
    assert data['message'] == 'Removed Friend or Friend Request'


@pytest.mark.django_db
def test_see_friend_list_fail(client, user, friends):
    response = client.get("/api/user/friends/see-friends-list/")
    data = response.data
    print(data)
    assert response.status_code == 401
    assert data["detail"] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_see_friend_list_success(client, user, friends, auth_user_client):
    response = client.get("/api/user/friends/see-friends-list/")
    data = response.data
    print(data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_search_friend_fail(client, user, second_user):
    search = "a"
    response = client.get("/api/user/friends/search-friend/")
    data = response.data
    assert response.status_code == 401
    assert data["detail"] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_search_friend_success(client, auth_user_client, second_user):
    search = "a"
    response = client.get("/api/user/friends/search-friend/")
    data = response.data
    assert response.status_code == 200
