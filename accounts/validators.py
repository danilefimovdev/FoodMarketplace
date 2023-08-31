import os.path

from PIL import Image
from django.core.exceptions import ValidationError


def allow_only_images_validator(value):
    ext = os.path.splitext(value.name)[1]  # cover-image.jpg
    valid_extensions = ['.jpg', '.png', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported file extensions. Allowed extensions: " + str(valid_extensions))


def allow_only_square_images_validator(value):
    im = Image.open(value)
    width, height = im.size
    print('size', width, height)
    if width != height:
        raise ValidationError("You can upload only square images")

