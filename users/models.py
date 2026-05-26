from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from core.models import TimeStampedModel
from core.validators import validate_image_file


class CustomUser(AbstractUser):
    """Extended user model with additional fields."""
    
    # Additional fields
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('vendor', 'Vendor/Business'),
        ('admin', 'Platform Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    
    # Address fields
    street_address = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=100, blank=True, verbose_name="City Area/Neighborhood")
    
    # Account status
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Override related names to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='customuser_set',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='customuser_set',
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_address(self):
        """Return formatted full address."""
        address_parts = [
            self.street_address,
            self.location
        ]
        return ', '.join([part for part in address_parts if part])

    def clean(self):
        """Validate user data."""
        super().clean()
        if self.email and CustomUser.objects.filter(
            email=self.email
        ).exclude(pk=self.pk).exists():
            raise ValidationError({'email': 'This email is already in use.'})
        if self.phone_number and len(self.phone_number) < 10:
            raise ValidationError({'phone_number': 'Phone number must be at least 10 digits.'})


class UserPreferences(TimeStampedModel):
    """User preferences and settings."""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='preferences')
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    order_updates = models.BooleanField(default=True)
    promotional_emails = models.BooleanField(default=True)
    
    # Privacy
    show_profile = models.BooleanField(default=False)
    allow_data_collection = models.BooleanField(default=False)
    
    # Preferences
    preferred_currency = models.CharField(max_length=3, default='USD')
    preferred_language = models.CharField(max_length=10, default='en')
    theme = models.CharField(
        max_length=20,
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light'
    )

    class Meta:
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'

    def __str__(self):
        return f"Preferences for {self.user.email}"


class Vendor(TimeStampedModel):
    """Profile model for third-party businesses selling on A.K.D."""
    
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='vendor_profile')
    shop_name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(
        upload_to='vendor_logos/',
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'gif']),
            validate_image_file,
        ]
    )
    banner = models.ImageField(
        upload_to='vendor_banners/',
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'gif']),
            validate_image_file,
        ]
    )
    
    # Verification & Status
    is_active = models.BooleanField(default=False)  # Requires platform admin verification to sell
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)  # Platform commission fee
    
    # Financial Connect (Stripe Payouts)
    stripe_connect_id = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Vendor Profile'
        verbose_name_plural = 'Vendor Profiles'

    def __str__(self):
        return f"{self.shop_name} (Owned by {self.owner.email})"
