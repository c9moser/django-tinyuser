from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _


class RestrictedImageField(models.ImageField):
    """
    A custom ImageField that restricts the allowed file types to common image formats.
    """

    def __init__(self, *args, max_file_size=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_content_types = [
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/webp',
        ]
        self.max_file_size = max_file_size

    def clean(self, value, model_instance):
        file = super().clean(value, model_instance)

        if file:
            content_type = file.file.content_type
            if content_type not in self.allowed_content_types:
                raise ValidationError(_('Unsupported file type. Allowed types are: %(types)s.'),
                                      params={'types': ', '.join(self.allowed_content_types)})

        return file


class RestrictedSvgImageFileField(RestrictedImageField):
    """
    A custom FileField that restricts the allowed file type to SVG images.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_content_types.append('image/svg+xml')

    def clean(self, value, model_instance):
        file = super().clean(value, model_instance)

        if file:
            content_type = file.file.content_type
            if content_type not in self.allowed_content_types:
                raise ValidationError(_('Unsupported file type. Only SVG images are allowed.'))

            if self.max_file_size and file.size > self.max_file_size:
                raise ValidationError(_('File size exceeds the maximum limit of %(max_file_size)s bytes.'),
                                      params={'max_file_size': self.max_file_size})

        return file
