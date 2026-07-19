from rest_framework import serializers

from common.serializers import CountrySerializer

from .models import StudentProfile, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "firebase_uid", "email", "full_name", "date_joined"]
        read_only_fields = fields


class StudentProfileSerializer(serializers.ModelSerializer):
    country_detail = CountrySerializer(source="country", read_only=True)

    class Meta:
        model = StudentProfile
        fields = ["id", "user", "phone", "country", "country_detail", "photo_public_id", "photo_url"]
        read_only_fields = ["id", "user", "country_detail", "photo_public_id", "photo_url"]


class MeSerializer(serializers.Serializer):
    user = UserSerializer()
    profile = StudentProfileSerializer()
