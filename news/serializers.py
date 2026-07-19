from rest_framework import serializers

from .models import Blog, FAQ, Inquiry, News


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ["id", "title", "slug", "body", "cover_public_id", "cover_url", "published_at"]


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ["id", "title", "slug", "body", "cover_public_id", "cover_url", "author", "tags", "published_at"]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id", "question", "answer", "category", "display_order"]


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ["id", "name", "email", "message", "created_at"]
        read_only_fields = ["created_at"]
