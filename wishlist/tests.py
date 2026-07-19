from rest_framework.test import APITestCase

from accounts.models import User
from common.models import Country, State
from universities.models import University

from .models import WishlistUniversity


class WishlistTests(APITestCase):
    def test_create_wishlist_university(self):
        user = User.objects.create(firebase_uid="wish-user", email="wish@example.com", full_name="Wish User")
        self.client.force_authenticate(user=user)
        country = Country.objects.create(name="Malaysia", code="MY")
        state = State.objects.create(country=country, name="Selangor")
        university = University.objects.create(
            name="Wishlist University",
            slug="wishlist-university",
            short_description="Short",
            full_description="Full",
            university_type=University.TYPE_PRIVATE,
            state=state,
        )

        response = self.client.post("/api/v1/wishlist/universities/", {"university": university.id}, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(WishlistUniversity.objects.count(), 1)

# Create your tests here.
