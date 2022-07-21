import pytest
from notifications.models import Notifications


@pytest.mark.django_db
def test_notification_model_create_pass(client, user, second_user):
    notification = Notifications.objects.create(notified_user=user,
                                                notified_by=second_user
                                                )
    assert notification.notified_user == user
    assert notification.notified_by == second_user


@pytest.mark.django_db
def test_notification_model_delete_pass(client, user, second_user):
    notification = Notifications.objects.create(notified_user=user,
                                                notified_by=second_user
                                                )
    notification_id = notification.id
    print(notification.id)
    payload = {
        "id": notification_id
    }
    Notifications.objects.get(**payload).delete()
