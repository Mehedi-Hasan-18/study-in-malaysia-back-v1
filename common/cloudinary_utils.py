from cloudinary import uploader


def upload_file(file, folder, resource_type="auto"):
    """
    Upload a file to Cloudinary and normalize the response fields every model stores.

    resource_type: "image" for photos/logos, "raw" for PDFs, "auto" when caller can accept Cloudinary detection.
    Returns: {public_id, secure_url, resource_type, format}
    """
    result = uploader.upload(file, folder=folder, resource_type=resource_type)

    return {
        "public_id": result["public_id"],
        "secure_url": result["secure_url"],
        "resource_type": result.get("resource_type", resource_type),
        "format": result.get("format", ""),
    }


def delete_file(public_id, resource_type="auto"):
    """Delete a Cloudinary asset by public_id."""
    if not public_id:
        return None

    return uploader.destroy(public_id, resource_type=resource_type)
