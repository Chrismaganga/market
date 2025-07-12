from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
# from django.contrib.gis.db import models as gis_models
# from django.contrib.gis.geos import Point


class User(AbstractUser):
    """Custom User model with extended profile fields."""
    
    # Basic profile fields
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Location fields
    # location = gis_models.PointField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Profile fields
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Verification fields
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)
    
    # Preferences
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
    
    def set_location(self, latitude, longitude):
        """Set user location from coordinates."""
        # if latitude and longitude:
        #     self.location = Point(longitude, latitude)
        pass
    
    def get_full_address(self):
        """Get formatted full address."""
        parts = [self.address, self.city, self.state, self.postal_code, self.country]
        return ', '.join(filter(None, parts))


class UserVerification(models.Model):
    """Model for storing user verification data."""
    
    VERIFICATION_TYPES = [
        ('email', 'Email Verification'),
        ('phone', 'Phone Verification'),
        ('identity', 'Identity Verification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    document = models.FileField(upload_to='verifications/', null=True, blank=True)
    notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verifications_approved')
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_verifications'
        unique_together = ['user', 'verification_type']
    
    def __str__(self):
        return f"{self.user.username} - {self.verification_type}" 