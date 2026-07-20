from rest_framework import serializers

from common.serializers import CloudinaryUploadMixin

from .models import Blog, FAQ, Inquiry, News


class NewsSerializer(CloudinaryUploadMixin, serializers.ModelSerializer):
    cover = serializers.ImageField(write_only=True, required=False)

    cloudinary_upload_fields = {
        "cover": {
            "folder": lambda instance: f"news/{instance.id}/cover/",
            "public_id_field": "cover_public_id",
            "url_field": "cover_url",
            "resource_type": "image",
        },
    }

    class Meta:
        model = News
        fields = ["id", "title", "slug", "body", "cover", "cover_public_id", "cover_url", "published_at"]
        read_only_fields = ["cover_public_id", "cover_url"]


class BlogSerializer(CloudinaryUploadMixin, serializers.ModelSerializer):
    cover = serializers.ImageField(write_only=True, required=False)

    cloudinary_upload_fields = {
        "cover": {
            "folder": lambda instance: f"blogs/{instance.id}/cover/",
            "public_id_field": "cover_public_id",
            "url_field": "cover_url",
            "resource_type": "image",
        },
    }

    class Meta:
        model = Blog
        fields = ["id", "title", "slug", "body", "cover", "cover_public_id", "cover_url", "author", "tags", "published_at"]
        read_only_fields = ["cover_public_id", "cover_url"]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id", "question", "answer", "category", "display_order"]


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ["id", "name", "email", "message", "created_at"]
        read_only_fields = ["created_at"]
