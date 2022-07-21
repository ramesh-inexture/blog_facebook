import pytest
from notifications.models import Notifications


@pytest.mark.django_db
def test_all_notifications_fail(client, user, second_user):
    for i in range(3):
        payload = {
            "notified_user": second_user,
            "notified_by": user,
            "header": f"notification_{i}",
            "body": f"body of notification_{i}"
        }
        Notifications.objects.create(**payload)
    response = client.get("/api/user/notifications/")
    data = response.data
    print(response.data)
    assert response.status_code == 401
    assert data["detail"] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_all_notifications_success(client, user, auth_user_client, second_user):
    for i in range(3):
        payload = {
            "notified_user": second_user,
            "notified_by": user,
            "header": f"notification_{i}",
            "body": f"body of notification_{i}"
        }
        Notifications.objects.create(**payload)
    response = client.get("/api/user/notifications/")
    data = response.data
    print(response.data)
    assert response.status_code == 200
