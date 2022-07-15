import pytest
from posts.models import Posts


@pytest.mark.django_db
def test_create_post_fail(client, auth_user_client):
    payload = {
        "title":""
    }
    response = client.post("/api/user/post/create_posts/", payload)
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
    assert response.status_code == 201


@pytest.mark.django_db
def test_list_posts_success(client, auth_user_client, user):
    user_id = user.id
    print(user_id)
    post_payload = {
        "title": "first post",
        "posted_by": user
    }
    post = Posts.objects.create(**post_payload)
    response = auth_user_client.get(f"/api/user/post/post-list/{user_id}/")
    data = response.data
    print(data)
    assert response.status_code == 200


"""
@pytest.mark.django_db
def test_delete_profile_fail_for_existing_order(user, auth_user_client):
    brand = Brand.objects.create(name="Tata", available=True)
    car_type = Type.objects.create(name="SUV", available=True)
    payload = {
        "name": "Nexon",
        "price": 2000,
        "reg_number": "GJ-01 EZ 5939",
        "brand": brand,
        "type": car_type,
        "available": True,
    }
    car = Car.objects.create(**payload)
    payload = {
        "user": user,
        "car": car,
        "start_date": '2022-07-13',
        "end_date": '2022-07-13',
        "price": 1000,
        "discount": 0,
        "payment_intent_id": 'abc',
        "fine_payment_intent_id": 'abc',
    }
    Order.objects.create(**payload)
    response = auth_user_client.delete("/auth/profile/")
    data = response.data
    assert response.status_code == 400
    assert data['message'] == DELETE_USER_EXISTING_BOOKINGS
    """