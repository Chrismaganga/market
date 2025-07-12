from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Listing, ListingImage, ListingFavorite, ListingView, ListingReport
from .serializers import (
    ListingSerializer, ListingDetailSerializer, ListingCreateSerializer,
    ListingUpdateSerializer, ListingImageSerializer, ListingFavoriteSerializer,
    ListingReportSerializer, ListingSearchSerializer
)
from .filters import ListingFilter
from .utils import (
    get_nearby_listings, get_trending_listings, get_featured_listings,
    get_similar_listings, get_seller_listings, calculate_listing_stats,
    get_listing_analytics, get_listing_recommendations
)


class ListingListView(generics.ListAPIView):
    """View for listing all active listings."""
    
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['title', 'description', 'city', 'state', 'country']
    ordering_fields = ['price', 'created_at', 'views_count', 'favorites_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Listing.objects.filter(
            status='active',
            is_active=True
        ).select_related('seller', 'category').prefetch_related('images')
        
        # Geo-based filtering
        latitude = self.request.query_params.get('latitude')
        longitude = self.request.query_params.get('longitude')
        radius = float(self.request.query_params.get('radius', 50))  # km
        
        if latitude and longitude:
            user_location = Point(float(longitude), float(latitude))
            queryset = queryset.filter(
                location__distance_lte=(user_location, radius / 100)  # Convert km to degrees
            ).annotate(
                distance=Distance('location', user_location)
            ).order_by('distance')
        
        return queryset


class ListingDetailView(generics.RetrieveAPIView):
    """View for listing details."""
    
    serializer_class = ListingDetailSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Listing.objects.select_related('seller', 'category').prefetch_related('images')
    lookup_field = "id"
    lookup_url_kwarg = "listing_id"
    
    def retrieve(self, request, *args, **kwargs):
        listing = self.get_object()
        
        # Increment view count
        listing.increment_views()
        
        # Log view
        ListingView.objects.create(
            listing=listing,
            user=request.user if request.user.is_authenticated else None,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return super().retrieve(request, *args, **kwargs)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ListingCreateView(generics.CreateAPIView):
    """View for creating listings."""
    
    serializer_class = ListingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()


class ListingUpdateView(generics.UpdateAPIView):
    """View for updating listings."""
    
    serializer_class = ListingUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Listing.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "listing_id"
    
    def get_queryset(self):
        return Listing.objects.filter(seller=self.request.user)


class ListingDeleteView(generics.DestroyAPIView):
    """View for deleting listings."""
    
    permission_classes = [permissions.IsAuthenticated]
    queryset = Listing.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "listing_id"
    
    def get_queryset(self):
        return Listing.objects.filter(seller=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = 'suspended'
        instance.save()


class ListingSearchView(APIView):
    """Advanced search view for listings."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = ListingSearchSerializer(data=request.data)
        if serializer.is_valid():
            params = serializer.validated_data
            
            queryset = Listing.objects.filter(
                status='active',
                is_active=True
            ).select_related('seller', 'category').prefetch_related('images')
            
            # Text search
            if params.get('query'):
                query = params['query']
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(city__icontains=query) |
                    Q(state__icontains=query)
                )
            
            # Category filter
            if params.get('category'):
                queryset = queryset.filter(category_id=params['category'])
            
            # Price range
            if params.get('min_price'):
                queryset = queryset.filter(price__gte=params['min_price'])
            if params.get('max_price'):
                queryset = queryset.filter(price__lte=params['max_price'])
            
            # Condition filter
            if params.get('condition'):
                queryset = queryset.filter(condition=params['condition'])
            
            # Geo-based search
            if params.get('latitude') and params.get('longitude'):
                user_location = Point(params['longitude'], params['latitude'])
                radius = params.get('radius', 50) / 100  # Convert km to degrees
                queryset = queryset.filter(
                    location__distance_lte=(user_location, radius)
                ).annotate(
                    distance=Distance('location', user_location)
                )
            
            # Sorting
            sort_by = params.get('sort_by', 'created_at')
            sort_order = params.get('sort_order', 'desc')
            
            if sort_order == 'desc':
                sort_by = f'-{sort_by}'
            
            if params.get('latitude') and params.get('longitude'):
                # If geo search is active, sort by distance first
                queryset = queryset.order_by('distance', sort_by)
            else:
                queryset = queryset.order_by(sort_by)
            
            # Pagination
            page = params.get('page', 1)
            page_size = params.get('page_size', 20)
            start = (page - 1) * page_size
            end = start + page_size
            
            total_count = queryset.count()
            listings = queryset[start:end]
            
            serializer = ListingSerializer(listings, many=True, context={'request': request})
            
            return Response({
                'results': serializer.data,
                'total_count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListingFavoriteView(generics.CreateAPIView):
    """View for favoriting listings."""
    
    serializer_class = ListingFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        # Update favorites count
        listing = serializer.instance.listing
        listing.favorites_count = listing.favorited_by.count()
        listing.save(update_fields=['favorites_count'])


class ListingUnfavoriteView(generics.DestroyAPIView):
    """View for unfavoriting listings."""
    
    permission_classes = [permissions.IsAuthenticated]
    queryset = ListingFavorite.objects.all()
    
    def get_queryset(self):
        return ListingFavorite.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        listing = instance.listing
        instance.delete()
        
        # Update favorites count
        listing.favorites_count = listing.favorited_by.count()
        listing.save(update_fields=['favorites_count'])


class UserFavoritesView(generics.ListAPIView):
    """View for user's favorite listings."""
    
    serializer_class = ListingFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ListingFavorite.objects.filter(user=self.request.user)


class UserListingsView(generics.ListAPIView):
    """View for user's own listings."""
    
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Listing.objects.filter(
            seller=self.request.user
        ).select_related('category').prefetch_related('images')


class ListingReportView(generics.CreateAPIView):
    """View for reporting listings."""
    
    serializer_class = ListingReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)


class ListingImageUploadView(generics.CreateAPIView):
    """View for uploading listing images."""
    
    serializer_class = ListingImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        listing_id = self.kwargs.get('listing_id')
        listing = get_object_or_404(Listing, id=listing_id, seller=self.request.user)
        serializer.save(listing=listing)


class ListingImageDeleteView(generics.DestroyAPIView):
    """View for deleting listing images."""
    
    permission_classes = [permissions.IsAuthenticated]
    queryset = ListingImage.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "image_id"
    
    def get_queryset(self):
        image_id = self.kwargs.get('image_id')
        return ListingImage.objects.filter(
            id=image_id,
            listing__seller=self.request.user
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_favorite(request, listing_id):
    """Toggle favorite status for a listing."""
    try:
        listing = Listing.objects.get(id=listing_id, status='active', is_active=True)
        favorite, created = ListingFavorite.objects.get_or_create(
            user=request.user,
            listing=listing
        )
        
        if not created:
            favorite.delete()
            is_favorited = False
        else:
            is_favorited = True
        
        # Update favorites count
        listing.favorites_count = listing.favorited_by.count()
        listing.save(update_fields=['favorites_count'])
        
        return Response({
            'is_favorited': is_favorited,
            'favorites_count': listing.favorites_count
        })
    
    except Listing.DoesNotExist:
        return Response(
            {'error': 'Listing not found'},
            status=status.HTTP_404_NOT_FOUND
        )


# Additional listing views
class TrendingListingsView(generics.ListAPIView):
    """View for trending listings."""
    
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        days = int(self.request.query_params.get('days', 7))
        limit = int(self.request.query_params.get('limit', 10))
        return get_trending_listings(days=days, limit=limit)


class FeaturedListingsView(generics.ListAPIView):
    """View for featured listings."""
    
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        limit = int(self.request.query_params.get('limit', 10))
        return get_featured_listings(limit=limit)


class NearbyListingsView(generics.ListAPIView):
    """View for nearby listings."""
    
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        latitude = float(self.request.query_params.get('latitude'))
        longitude = float(self.request.query_params.get('longitude'))
        radius = float(self.request.query_params.get('radius', 50))
        limit = int(self.request.query_params.get('limit', 20))
        
        return get_nearby_listings(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            limit=limit
        )


class SimilarListingsView(generics.ListAPIView):
    """View for similar listings."""
    
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        listing_id = self.kwargs.get('listing_id')
        listing = get_object_or_404(Listing, id=listing_id)
        limit = int(self.request.query_params.get('limit', 5))
        
        return get_similar_listings(listing=listing, limit=limit)


class SellerListingsView(generics.ListAPIView):
    """View for seller's other listings."""
    
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        seller_id = self.kwargs.get('seller_id')
        exclude_listing_id = self.request.query_params.get('exclude_listing')
        limit = int(self.request.query_params.get('limit', 10))
        
        from apps.users.models import User
        seller = get_object_or_404(User, id=seller_id)
        exclude_listing = None
        
        if exclude_listing_id:
            exclude_listing = get_object_or_404(Listing, id=exclude_listing_id)
        
        return get_seller_listings(
            seller=seller,
            exclude_listing=exclude_listing,
            limit=limit
        )


class ListingRecommendationsView(generics.ListAPIView):
    """View for personalized listing recommendations."""
    
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        limit = int(self.request.query_params.get('limit', 10))
        return get_listing_recommendations(user=self.request.user, limit=limit)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def listing_stats(request, listing_id):
    """Get statistics for a listing."""
    listing = get_object_or_404(Listing, id=listing_id)
    
    # Check if user is the seller
    if listing.seller != request.user:
        return Response(
            {'error': 'Access denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    stats = calculate_listing_stats(listing)
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def listing_analytics(request, listing_id):
    """Get analytics for a listing."""
    listing = get_object_or_404(Listing, id=listing_id)
    
    # Check if user is the seller
    if listing.seller != request.user:
        return Response(
            {'error': 'Access denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    days = int(request.query_params.get('days', 30))
    analytics = get_listing_analytics(listing=listing, days=days)
    return Response(analytics) 