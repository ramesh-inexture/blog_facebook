import pytest
from Friends.models import Friends


@pytest.mark.django_db
def test_friends_model_create(client, user, second_user):
    friend = Friends.objects.create(sender_id=user,
                                    receiver_id=second_user
                                    )
    assert friend.sender_id == user
    assert friend.receiver_id == second_user


@pytest.mark.django_db
def test_friends_model_delete(client, user, second_user):
    friend = Friends.objects.create(sender_id=user,
                                    receiver_id=second_user
                                    )
    payload = {
        "sender_id": user.id,
        "receiver_id": second_user.id
    }
    Friends.objects.get(**payload).delete()
    assert Friends.objects.all().count() == 0

