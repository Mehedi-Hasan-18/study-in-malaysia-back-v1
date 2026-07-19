from rest_framework import serializers

from common.serializers import CitySerializer, StateSerializer

from .models import Gallery, University


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ["id", "university", "image_public_id", "image_url", "caption", "display_order"]


class UniversitySerializer(serializers.ModelSerializer):
    state_detail = StateSerializer(source="state", read_only=True)
    city_detail = CitySerializer(source="city", read_only=True)
    gallery = GallerySerializer(many=True, read_only=True)

    class Meta:
        model = University
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "full_description",
            "university_type",
            "state",
            "state_detail",
            "city",
            "city_detail",
            "ranking_tier",
            "is_featured",
            "logo_public_id",
            "logo_url",
            "cover_public_id",
            "cover_url",
            "website",
            "contact_email",
            "contact_phone",
            "established_year",
            "total_students",
            "gallery",
        ]
