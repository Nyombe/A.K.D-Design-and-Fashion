import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class ComplexityValidator:
    """
    Validator to ensure password has a mix of uppercase, lowercase,
    numbers and symbols.
    """
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("The password must contain at least one uppercase letter."),
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("The password must contain at least one lowercase letter."),
                code='password_no_lower',
            )
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("The password must contain at least one number."),
                code='password_no_number',
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_]', password):
            raise ValidationError(
                _("The password must contain at least one symbol (!@#$%^&*(),.?\":{}|<>_)."),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one uppercase letter, "
            "one lowercase letter, one number, and one symbol."
        )


def validate_image_file(upload):
    """Validate uploaded image file size and extension.

    Raises a ValidationError when the file is too large or has an
    unsupported extension. Uses settings.ALLOWED_IMAGE_EXTENSIONS.
    """
    from django.conf import settings
    from django.core.exceptions import ValidationError

    # If no file was provided (blank=True), allow it
    if not upload:
        return

    # Size check (default: FILE_UPLOAD_MAX_MEMORY_SIZE or 5 MB)
    max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 5 * 1024 * 1024)
    try:
        size = upload.size
    except Exception:
        # If the storage backend doesn't provide size, skip strict size check
        size = None

    if size and size > max_size:
        raise ValidationError(f'File too large (max {int(max_size/1024/1024)}MB).')

    # Extension check
    name = getattr(upload, 'name', '') or ''
    ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
    allowed = getattr(settings, 'ALLOWED_IMAGE_EXTENSIONS', ['jpg', 'jpeg', 'png', 'gif', 'webp'])
    if ext and ext not in allowed:
        raise ValidationError(f'Unsupported file extension: {ext}')

