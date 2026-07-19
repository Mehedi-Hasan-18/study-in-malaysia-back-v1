from rest_framework.test import APITestCase

from accounts.models import User

from .models import Notification


class NotificationTests(APITestCase):
    def test_mark_notification_read(self):
        user = User.objects.create(firebase_uid="notify-user", email="notify@example.com", full_name="Notify User")
        self.client.force_authenticate(user=user)
        notification = Notification.objects.create(user=user, message="Application approved")

        response = self.client.put(f"/api/v1/notifications/{notification.id}/read/")

        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

# Create your tests here.
