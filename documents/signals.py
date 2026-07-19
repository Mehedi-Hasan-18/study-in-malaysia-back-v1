from django.db.models.signals import pre_delete
from django.dispatch import receiver

from common.cloudinary_utils import delete_file

from .models import ApplicationDocument


@receiver(pre_delete, sender=ApplicationDocument)
def delete_cloudinary_file(sender, instance, **kwargs):
    if instance.file_public_id:
        delete_file(instance.file_public_id, resource_type=instance.resource_type)
