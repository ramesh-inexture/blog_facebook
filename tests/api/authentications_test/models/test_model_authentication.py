import pytest
from authentication.models import User, RestrictedUsers


@pytest.mark.django_db
def test_create_user_model(client):
    user = User.objects.create_user(first_name="ramsingh",
                                    email="ramesh@gmail.com",
                                    password="Rames@1234"
                                    )
    assert user.first_name == "ramsingh"


@pytest.mark.django_db
def test_update_user_model(client):
    user = User.objects.create_user(first_name="ramsingh",
                                    email="ramesh@gmail.com",
                                    password="Rames@1234"
                                    )
    user.first_name = "azhar"
    user.save()
    assert user.first_name == "azhar"


@pytest.mark.django_db
def test_delete_user_model(client):
    user = User.objects.create_user(first_name="ramsingh",
                                    email="ramesh@gmail.com",
                                    password="Rames@1234"
                                    )
    User.objects.get(id=user.id).delete()


@pytest.mark.django_db
def test_restricted_user_model(client, user, second_user):
    restrict_user = RestrictedUsers.objects.create(blocked_user=user,
                                                   blocked_by=second_user
                                                   )
    assert restrict_user.blocked_user == user


@pytest.mark.django_db
def test_delete_restricted_user_model(client, user, second_user):
    restrict_user = RestrictedUsers.objects.create(blocked_user=user,
                                                   blocked_by=second_user
                                                   )
    RestrictedUsers.objects.get(id=restrict_user.id).delete()