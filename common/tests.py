from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from .cloudinary_utils import delete_file, upload_file


class CloudinaryUtilsTests(SimpleTestCase):
    @patch("common.cloudinary_utils.uploader.upload")
    def test_upload_file_returns_storage_fields(self, mocked_upload):
        mocked_upload.return_value = {
            "public_id": "profiles/1/photo/avatar",
            "secure_url": "https://res.cloudinary.com/demo/image/upload/avatar.jpg",
            "resource_type": "image",
            "format": "jpg",
        }

        result = upload_file("file-bytes", "profiles/1/photo/", resource_type="image")

        mocked_upload.assert_called_once_with(
            "file-bytes",
            folder="profiles/1/photo/",
            resource_type="image",
        )
        self.assertEqual(
            result,
            {
                "public_id": "profiles/1/photo/avatar",
                "secure_url": "https://res.cloudinary.com/demo/image/upload/avatar.jpg",
                "resource_type": "image",
                "format": "jpg",
            },
        )

    @patch("common.cloudinary_utils.uploader.destroy")
    def test_delete_file_skips_empty_public_id(self, mocked_destroy):
        result = delete_file("", resource_type="raw")

        self.assertIsNone(result)
        mocked_destroy.assert_not_called()

    @patch("common.cloudinary_utils.uploader.destroy")
    def test_delete_file_passes_public_id_and_resource_type(self, mocked_destroy):
        mocked_destroy.return_value = Mock()

        delete_file("applications/1/passport/file", resource_type="raw")

        mocked_destroy.assert_called_once_with(
            "applications/1/passport/file",
            resource_type="raw",
        )
