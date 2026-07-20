from rest_framework import serializers

from common.cloudinary_utils import upload_file
from common.serializers import CitySerializer, CloudinaryUploadMixin, StateSerializer

from .models import Gallery, University


class GallerySerializer(CloudinaryUploadMixin, serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)

    cloudinary_upload_fields = {
        "image": {
            "folder": lambda instance: f"universities/{instance.university_id}/gallery/",
            "public_id_field": "image_public_id",
            "url_field": "image_url",
            "resource_type": "image",
        },
    }

    class Meta:
        model = Gallery
        fields = ["id", "university", "image", "image_public_id", "image_url", "caption", "display_order"]
        read_only_fields = ["image_public_id", "image_url"]

    def create(self, validated_data):
        uploaded_image = validated_data.pop("image")
        result = upload_file(
            uploaded_image,
            f"universities/{validated_data['university'].id}/gallery/",
            resource_type="image",
        )
        validated_data["image_public_id"] = result["public_id"]
        validated_data["image_url"] = result["secure_url"]
        return super(CloudinaryUploadMixin, self).create(validated_data)


class UniversitySerializer(CloudinaryUploadMixin, serializers.ModelSerializer):
    state_detail = StateSerializer(source="state", read_only=True)
    city_detail = CitySerializer(source="city", read_only=True)
    gallery = GallerySerializer(many=True, read_only=True)
    logo = serializers.ImageField(write_only=True, required=False)
    cover = serializers.ImageField(write_only=True, required=False)

    cloudinary_upload_fields = {
        "logo": {
            "folder": lambda instance: f"universities/{instance.id}/logo/",
            "public_id_field": "logo_public_id",
            "url_field": "logo_url",
            "resource_type": "image",
        },
        "cover": {
            "folder": lambda instance: f"universities/{instance.id}/cover/",
            "public_id_field": "cover_public_id",
            "url_field": "cover_url",
            "resource_type": "image",
        },
    }

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
            "logo",
            "logo_public_id",
            "logo_url",
            "cover",
            "cover_public_id",
            "cover_url",
            "website",
            "contact_email",
            "contact_phone",
            "established_year",
            "total_students",
            "gallery",
        ]
        read_only_fields = ["logo_public_id", "logo_url", "cover_public_id", "cover_url"]
