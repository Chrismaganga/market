from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    # Listings
    path('', views.ListingListView.as_view(), name='listing-list'),
    path('create/', views.ListingCreateView.as_view(), name='listing-create'),
    path('<int:listing_id>/', views.ListingDetailView.as_view(), name='listing-detail'),
    path('<int:listing_id>/update/', views.ListingUpdateView.as_view(), name='listing-update'),
    path('<int:listing_id>/delete/', views.ListingDeleteView.as_view(), name='listing-delete'),
    
    # Search and Discovery
    path('search/', views.ListingSearchView.as_view(), name='listing-search'),
    path('trending/', views.TrendingListingsView.as_view(), name='trending-listings'),
    path('featured/', views.FeaturedListingsView.as_view(), name='featured-listings'),
    path('nearby/', views.NearbyListingsView.as_view(), name='nearby-listings'),
    path('recommendations/', views.ListingRecommendationsView.as_view(), name='listing-recommendations'),
    
    # Related listings
    path('<int:listing_id>/similar/', views.SimilarListingsView.as_view(), name='similar-listings'),
    path('seller/<int:seller_id>/', views.SellerListingsView.as_view(), name='seller-listings'),
    
    # Favorites
    path('<int:listing_id>/favorite/', views.toggle_favorite, name='listing-favorite'),
    path('favorites/', views.UserFavoritesView.as_view(), name='user-favorites'),
    
    # User listings
    path('my-listings/', views.UserListingsView.as_view(), name='user-listings'),
    
    # Reports
    path('<int:listing_id>/report/', views.ListingReportView.as_view(), name='listing-report'),
    
    # Images
    path('<int:listing_id>/images/', views.ListingImageUploadView.as_view(), name='listing-image-upload'),
    path('images/<int:image_id>/delete/', views.ListingImageDeleteView.as_view(), name='listing-image-delete'),
    
    # Analytics (seller only)
    path('<int:listing_id>/stats/', views.listing_stats, name='listing-stats'),
    path('<int:listing_id>/analytics/', views.listing_analytics, name='listing-analytics'),
] 