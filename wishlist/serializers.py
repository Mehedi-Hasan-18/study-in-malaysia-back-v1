from rest_framework import serializers

from scholarships.serializers import ScholarshipSerializer
from universities.serializers import UniversitySerializer

from .models import WishlistScholarship, WishlistUniversity


class WishlistUniversitySerializer(serializers.ModelSerializer):
    university_detail = UniversitySerializer(source="university", read_only=True)

    class Meta:
        model = WishlistUniversity
        fields = ["id", "user", "university", "university_detail", "created_at"]
        read_only_fields = ["user", "university_detail", "created_at"]


class WishlistScholarshipSerializer(serializers.ModelSerializer):
    scholarship_detail = ScholarshipSerializer(source="scholarship", read_only=True)

    class Meta:
        model = WishlistScholarship
        fields = ["id", "user", "scholarship", "scholarship_detail", "created_at"]
        read_only_fields = ["user", "scholarship_detail", "created_at"]
