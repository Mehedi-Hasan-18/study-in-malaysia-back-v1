from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from common.cloudinary_utils import delete_file, upload_file


class Command(BaseCommand):
    help = "Upload a local file to Cloudinary through common.cloudinary_utils, then optionally delete it."

    def add_arguments(self, parser):
        parser.add_argument("file_path", help="Path to local file to upload.")
        parser.add_argument(
            "--folder",
            default="test/uploads/",
            help="Cloudinary folder. Default: test/uploads/",
        )
        parser.add_argument(
            "--resource-type",
            default="auto",
            choices=["auto", "image", "raw"],
            help="Cloudinary resource_type. Use image for photos/logos, raw for PDFs.",
        )
        parser.add_argument(
            "--keep",
            action="store_true",
            help="Keep uploaded file in Cloudinary. Default deletes after successful upload.",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file_path"])
        if not file_path.exists() or not file_path.is_file():
            raise CommandError(f"File not found: {file_path}")

        with file_path.open("rb") as file_obj:
            result = upload_file(
                file_obj,
                folder=options["folder"],
                resource_type=options["resource_type"],
            )

        self.stdout.write(self.style.SUCCESS("Cloudinary upload OK"))
        self.stdout.write(f"public_id: {result['public_id']}")
        self.stdout.write(f"secure_url: {result['secure_url']}")
        self.stdout.write(f"resource_type: {result['resource_type']}")
        self.stdout.write(f"format: {result['format']}")

        if not options["keep"]:
            delete_file(result["public_id"], resource_type=result["resource_type"])
            self.stdout.write(self.style.SUCCESS("Cloudinary delete OK"))
