from django.db import models
# from django.contrib.gis.db import models as gis_models
# from django.contrib.gis.geos import Point
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.users.models import User
from apps.categories.models import Category
import os
os.environ['GDAL_LIBRARY_PATH'] = '/usr/lib/libgdal.so'  # Use the actual path found above


class Listing(models.Model):
    """Model for marketplace listings."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
    ]
    
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Category and condition
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='listings')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    
    # Location
    # location = gis_models.PointField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Seller information
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    
    # Status and visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_negotiable = models.BooleanField(default=True)
    
    # Contact information
    contact_phone = models.CharField(max_length=17, blank=True)
    contact_email = models.EmailField(blank=True)
    
    # Attributes (JSON field for dynamic attributes)
    attributes = models.JSONField(default=dict, blank=True)
    
    # Statistics
    views_count = models.PositiveIntegerField(default=0)
    favorites_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'listings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Set expiration date if not set and status is active
        if self.status == 'active' and not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)
    
    def set_location(self, latitude, longitude):
        """Set listing location from coordinates."""
        # if latitude and longitude:
        #     self.location = Point(longitude, latitude)
        pass
    
    def get_full_address(self):
        """Get formatted full address."""
        parts = [self.address, self.city, self.state, self.postal_code, self.country]
        return ', '.join(filter(None, parts))
    
    def increment_views(self):
        """Increment view count."""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def is_expired(self):
        """Check if listing is expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def get_distance_from_point(self, point):
        """Get distance from a given point in kilometers."""
        # if self.location and point:
        #     return self.location.distance(point) * 100  # Convert to km
        return None


class ListingImage(models.Model):
    """Model for listing images."""
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listing_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'listing_images'
        ordering = ['is_primary', 'sort_order', 'created_at']
    
    def __str__(self):
        return f"{self.listing.title} - Image {self.id}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per listing
        if self.is_primary:
            ListingImage.objects.filter(
                listing=self.listing,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)


class ListingFavorite(models.Model):
    """Model for user favorites."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'listing_favorites'
        unique_together = ['user', 'listing']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.listing.title}"


class ListingView(models.Model):
    """Model for tracking listing views."""
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='view_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='viewed_listings')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'listing_views'
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f"{self.listing.title} - {self.viewed_at}"


class ListingReport(models.Model):
    """Model for listing reports."""
    
    REPORT_TYPES = [
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('fake', 'Fake Item'),
        ('scam', 'Scam'),
        ('duplicate', 'Duplicate Listing'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_filed')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_reviewed'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'listing_reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.listing.title} - {self.report_type}" 