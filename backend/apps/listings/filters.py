import django_filters
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import Listing


class ListingFilter(django_filters.FilterSet):
    """Custom filter for listings."""
    
    # Price range
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Category
    category = django_filters.NumberFilter(field_name='category__id')
    category_slug = django_filters.CharFilter(field_name='category__slug')
    
    # Location
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')
    state = django_filters.CharFilter(field_name='state', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='country', lookup_expr='icontains')
    
    # Condition
    condition = django_filters.ChoiceFilter(choices=Listing.CONDITION_CHOICES)
    
    # Seller
    seller = django_filters.NumberFilter(field_name='seller__id')
    seller_username = django_filters.CharFilter(field_name='seller__username', lookup_expr='icontains')
    
    # Features
    is_featured = django_filters.BooleanFilter()
    is_negotiable = django_filters.BooleanFilter()
    
    # Date range
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Search
    search = django_filters.CharFilter(method='search_filter')
    
    # Geo-based filtering
    latitude = django_filters.NumberFilter(method='geo_filter')
    longitude = django_filters.NumberFilter(method='geo_filter')
    radius = django_filters.NumberFilter(method='geo_filter')
    
    class Meta:
        model = Listing
        fields = {
            'status': ['exact'],
            'is_active': ['exact'],
        }
    
    def search_filter(self, queryset, name, value):
        """Search in title, description, and location."""
        return queryset.filter(
            django_filters.Q(title__icontains=value) |
            django_filters.Q(description__icontains=value) |
            django_filters.Q(city__icontains=value) |
            django_filters.Q(state__icontains=value) |
            django_filters.Q(country__icontains=value)
        )
    
    def geo_filter(self, queryset, name, value):
        """Filter by geographic location."""
        # This method will be called for latitude, longitude, and radius
        # We need to get all three values to perform the filter
        latitude = self.data.get('latitude')
        longitude = self.data.get('longitude')
        radius = self.data.get('radius', 50)  # Default 50km
        
        if latitude and longitude:
            user_location = Point(float(longitude), float(latitude))
            # Convert km to degrees (approximate)
            radius_degrees = radius / 100
            return queryset.filter(
                location__distance_lte=(user_location, radius_degrees)
            ).annotate(
                distance=Distance('location', user_location)
            ).order_by('distance')
        
        return queryset


class ListingSearchFilter(django_filters.FilterSet):
    """Advanced search filter for listings."""
    
    query = django_filters.CharFilter(method='search_query')
    category_ids = django_filters.BaseInFilter(field_name='category__id')
    price_range = django_filters.RangeFilter(field_name='price')
    conditions = django_filters.BaseInFilter(field_name='condition')
    
    class Meta:
        model = Listing
        fields = ['status', 'is_active', 'is_featured']
    
    def search_query(self, queryset, name, value):
        """Advanced search query."""
        if not value:
            return queryset
        
        return queryset.filter(
            django_filters.Q(title__icontains=value) |
            django_filters.Q(description__icontains=value) |
            django_filters.Q(category__name__icontains=value) |
            django_filters.Q(seller__username__icontains=value) |
            django_filters.Q(city__icontains=value) |
            django_filters.Q(state__icontains=value)
        ) 