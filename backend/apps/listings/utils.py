from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Listing, ListingView, ListingFavorite


def get_nearby_listings(latitude, longitude, radius=50, limit=20):
    """Get listings within a specified radius."""
    if not latitude or not longitude:
        return Listing.objects.none()
    
    user_location = Point(longitude, latitude)
    radius_degrees = radius / 100  # Convert km to degrees
    
    return Listing.objects.filter(
        status='active',
        is_active=True,
        location__distance_lte=(user_location, radius_degrees)
    ).annotate(
        distance=Distance('location', user_location)
    ).order_by('distance')[:limit]


def get_trending_listings(days=7, limit=10):
    """Get trending listings based on views and favorites."""
    cutoff_date = timezone.now() - timedelta(days=days)
    
    return Listing.objects.filter(
        status='active',
        is_active=True,
        created_at__gte=cutoff_date
    ).annotate(
        recent_views=Count('view_logs', filter=Q(view_logs__viewed_at__gte=cutoff_date)),
        recent_favorites=Count('favorited_by', filter=Q(favorited_by__created_at__gte=cutoff_date))
    ).order_by('-recent_views', '-recent_favorites')[:limit]


def get_featured_listings(limit=10):
    """Get featured listings."""
    return Listing.objects.filter(
        status='active',
        is_active=True,
        is_featured=True
    ).order_by('-created_at')[:limit]


def get_similar_listings(listing, limit=5):
    """Get similar listings based on category and price range."""
    price_range = listing.price * 0.3  # 30% price range
    
    return Listing.objects.filter(
        status='active',
        is_active=True,
        category=listing.category,
        price__range=(listing.price - price_range, listing.price + price_range)
    ).exclude(id=listing.id).order_by('-created_at')[:limit]


def get_seller_listings(seller, exclude_listing=None, limit=10):
    """Get other listings from the same seller."""
    queryset = Listing.objects.filter(
        seller=seller,
        status='active',
        is_active=True
    )
    
    if exclude_listing:
        queryset = queryset.exclude(id=exclude_listing.id)
    
    return queryset.order_by('-created_at')[:limit]


def calculate_listing_stats(listing):
    """Calculate statistics for a listing."""
    stats = {
        'total_views': listing.views_count,
        'total_favorites': listing.favorites_count,
        'avg_price_in_category': 0,
        'similar_listings_count': 0,
    }
    
    # Calculate average price in category
    avg_price = Listing.objects.filter(
        category=listing.category,
        status='active',
        is_active=True
    ).aggregate(avg_price=Avg('price'))['avg_price']
    
    if avg_price:
        stats['avg_price_in_category'] = float(avg_price)
    
    # Count similar listings
    price_range = listing.price * 0.3
    similar_count = Listing.objects.filter(
        category=listing.category,
        price__range=(listing.price - price_range, listing.price + price_range),
        status='active',
        is_active=True
    ).exclude(id=listing.id).count()
    
    stats['similar_listings_count'] = similar_count
    
    return stats


def update_listing_views(listing, user=None, ip_address=None, user_agent=None):
    """Update listing view count and create view log."""
    listing.increment_views()
    
    # Create view log
    ListingView.objects.create(
        listing=listing,
        user=user,
        ip_address=ip_address,
        user_agent=user_agent
    )


def get_listing_analytics(listing, days=30):
    """Get analytics for a listing."""
    cutoff_date = timezone.now() - timedelta(days=days)
    
    # Daily views
    daily_views = ListingView.objects.filter(
        listing=listing,
        viewed_at__gte=cutoff_date
    ).extra(
        select={'day': 'date(viewed_at)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Views by location
    location_views = ListingView.objects.filter(
        listing=listing,
        viewed_at__gte=cutoff_date
    ).values('ip_address').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Referrer analysis (if available)
    referrer_views = ListingView.objects.filter(
        listing=listing,
        viewed_at__gte=cutoff_date
    ).values('user_agent').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    return {
        'daily_views': list(daily_views),
        'location_views': list(location_views),
        'referrer_views': list(referrer_views),
        'total_views_period': daily_views.count(),
        'unique_visitors': ListingView.objects.filter(
            listing=listing,
            viewed_at__gte=cutoff_date
        ).values('ip_address').distinct().count(),
    }


def search_listings_advanced(query, filters=None, user_location=None, limit=20):
    """Advanced search function for listings."""
    queryset = Listing.objects.filter(
        status='active',
        is_active=True
    )
    
    # Text search
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(seller__username__icontains=query) |
            Q(city__icontains=query) |
            Q(state__icontains=query)
        )
    
    # Apply filters
    if filters:
        if 'category' in filters:
            queryset = queryset.filter(category_id=filters['category'])
        
        if 'min_price' in filters:
            queryset = queryset.filter(price__gte=filters['min_price'])
        
        if 'max_price' in filters:
            queryset = queryset.filter(price__lte=filters['max_price'])
        
        if 'condition' in filters:
            queryset = queryset.filter(condition=filters['condition'])
        
        if 'is_featured' in filters:
            queryset = queryset.filter(is_featured=filters['is_featured'])
    
    # Geo-based sorting
    if user_location:
        queryset = queryset.annotate(
            distance=Distance('location', user_location)
        ).order_by('distance')
    else:
        queryset = queryset.order_by('-created_at')
    
    return queryset[:limit]


def get_listing_recommendations(user, limit=10):
    """Get personalized listing recommendations for a user."""
    if not user.is_authenticated:
        return get_trending_listings(limit=limit)
    
    # Get user's favorite categories
    favorite_categories = ListingFavorite.objects.filter(
        user=user
    ).values('listing__category').annotate(
        count=Count('id')
    ).order_by('-count')[:3]
    
    category_ids = [item['listing__category'] for item in favorite_categories]
    
    if category_ids:
        # Get listings from favorite categories
        recommendations = Listing.objects.filter(
            category_id__in=category_ids,
            status='active',
            is_active=True
        ).exclude(
            favorited_by=user
        ).order_by('-created_at')[:limit]
        
        if recommendations.count() >= limit:
            return recommendations
    
    # Fallback to trending listings
    return get_trending_listings(limit=limit) 