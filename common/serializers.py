from rest_framework import serializers

from common.cloudinary_utils import delete_file, upload_file

from .models import City, Country, State


class CloudinaryUploadMixin:
    cloudinary_upload_fields = {}

    def _upload_cloudinary_files(self, instance, uploaded_files, old_public_ids=None):
        old_public_ids = old_public_ids or {}
        for upload_field, config in self.cloudinary_upload_fields.items():
            uploaded_file = uploaded_files.get(upload_field)
            if not uploaded_file:
                continue

            folder = config["folder"](instance)
            resource_type = config.get("resource_type", "auto")
            public_id_field = config["public_id_field"]
            url_field = config["url_field"]

            result = upload_file(uploaded_file, folder, resource_type=resource_type)
            setattr(instance, public_id_field, result["public_id"])
            setattr(instance, url_field, result["secure_url"])

            old_public_id = old_public_ids.get(public_id_field)
            if old_public_id and old_public_id != result["public_id"]:
                delete_file(old_public_id, resource_type=resource_type)

        if uploaded_files:
            instance.save()

        return instance

    def create(self, validated_data):
        uploaded_files = {
            field: validated_data.pop(field)
            for field in self.cloudinary_upload_fields
            if field in validated_data
        }
        instance = super().create(validated_data)
        return self._upload_cloudinary_files(instance, uploaded_files)

    def update(self, instance, validated_data):
        uploaded_files = {
            field: validated_data.pop(field)
            for field in self.cloudinary_upload_fields
            if field in validated_data
        }
        old_public_ids = {
            config["public_id_field"]: getattr(instance, config["public_id_field"], "")
            for config in self.cloudinary_upload_fields.values()
            if config["public_id_field"]
        }
        instance = super().update(instance, validated_data)
        return self._upload_cloudinary_files(instance, uploaded_files, old_public_ids)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name", "code"]


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ["id", "country", "name"]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "state", "name"]
