from rest_framework import serializers
from django.contrib.gis.geos import Point
from .models import Listing, ListingImage, ListingFavorite, ListingView, ListingReport
from apps.users.serializers import UserProfileSerializer
from apps.categories.serializers import CategorySerializer


class ListingImageSerializer(serializers.ModelSerializer):
    """Serializer for listing images."""
    
    class Meta:
        model = ListingImage
        fields = ['id', 'image', 'caption', 'is_primary', 'sort_order', 'created_at']


class ListingSerializer(serializers.ModelSerializer):
    """Basic serializer for listings."""
    
    seller = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    images_count = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'price', 'currency',
            'category', 'condition', 'seller', 'status', 'is_active',
            'is_featured', 'is_negotiable', 'location', 'address',
            'city', 'state', 'country', 'postal_code', 'primary_image',
            'images_count', 'views_count', 'favorites_count',
            'is_favorited', 'distance', 'created_at', 'updated_at'
        ]
        read_only_fields = ['views_count', 'favorites_count', 'created_at', 'updated_at']
    
    def get_primary_image(self, obj):
        """Get the primary image URL."""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return self.context['request'].build_absolute_uri(primary_image.image.url)
        # Return first image if no primary
        first_image = obj.images.first()
        if first_image:
            return self.context['request'].build_absolute_uri(first_image.image.url)
        return None
    
    def get_images_count(self, obj):
        """Get count of images."""
        return obj.images.count()
    
    def get_is_favorited(self, obj):
        """Check if current user has favorited this listing."""
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.favorited_by.filter(user=user).exists()
        return False
    
    def get_distance(self, obj):
        """Get distance from user's location."""
        user = self.context['request'].user
        if user.is_authenticated and user.location and obj.location:
            return obj.get_distance_from_point(user.location)
        return None


class ListingDetailSerializer(ListingSerializer):
    """Detailed serializer for listings."""
    
    images = ListingImageSerializer(many=True, read_only=True)
    full_address = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta(ListingSerializer.Meta):
        fields = ListingSerializer.Meta.fields + ['images', 'full_address', 'is_expired', 'attributes']
    
    def get_full_address(self, obj):
        """Get formatted full address."""
        return obj.get_full_address()
    
    def get_is_expired(self, obj):
        """Check if listing is expired."""
        return obj.is_expired()


class ListingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating listings."""
    
    images = ListingImageSerializer(many=True, required=False)
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)
    
    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'price', 'currency', 'category',
            'condition', 'is_negotiable', 'contact_phone', 'contact_email',
            'address', 'city', 'state', 'country', 'postal_code',
            'latitude', 'longitude', 'attributes', 'images'
        ]
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        
        # Set seller
        validated_data['seller'] = self.context['request'].user
        
        # Set location
        if latitude and longitude:
            validated_data['location'] = Point(longitude, latitude)
        
        # Create listing
        listing = Listing.objects.create(**validated_data)
        
        # Create images
        for image_data in images_data:
            ListingImage.objects.create(listing=listing, **image_data)
        
        return listing


class ListingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating listings."""
    
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)
    
    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'price', 'currency', 'category',
            'condition', 'is_negotiable', 'contact_phone', 'contact_email',
            'address', 'city', 'state', 'country', 'postal_code',
            'latitude', 'longitude', 'attributes'
        ]
    
    def update(self, instance, validated_data):
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        
        # Update location
        if latitude and longitude:
            instance.set_location(latitude, longitude)
        
        return super().update(instance, validated_data)


class ListingFavoriteSerializer(serializers.ModelSerializer):
    """Serializer for listing favorites."""
    
    listing = ListingSerializer(read_only=True)
    
    class Meta:
        model = ListingFavorite
        fields = ['id', 'listing', 'created_at']
        read_only_fields = ['created_at']


class ListingReportSerializer(serializers.ModelSerializer):
    """Serializer for listing reports."""
    
    reporter = UserProfileSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    
    class Meta:
        model = ListingReport
        fields = [
            'id', 'listing', 'reporter', 'report_type', 'description',
            'status', 'created_at'
        ]
        read_only_fields = ['reporter', 'status', 'created_at']


class ListingSearchSerializer(serializers.Serializer):
    """Serializer for listing search parameters."""
    
    query = serializers.CharField(required=False)
    category = serializers.IntegerField(required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    condition = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    radius = serializers.FloatField(required=False, default=50)  # km
    sort_by = serializers.CharField(required=False, default='created_at')
    sort_order = serializers.CharField(required=False, default='desc')
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=20) 