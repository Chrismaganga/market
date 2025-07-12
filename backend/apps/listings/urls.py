from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    # Listings
    path('', views.ListingListView.as_view(), name='listing-list'),
    path('create/', views.ListingCreateView.as_view(), name='listing-create'),
    path('<int:pk>/', views.ListingDetailView.as_view(), name='listing-detail'),
    path('<int:pk>/update/', views.ListingUpdateView.as_view(), name='listing-update'),
    path('<int:pk>/delete/', views.ListingDeleteView.as_view(), name='listing-delete'),
    
    # Search
    path('search/', views.ListingSearchView.as_view(), name='listing-search'),
    
    # Favorites
    path('<int:listing_id>/favorite/', views.toggle_favorite, name='listing-favorite'),
    path('favorites/', views.UserFavoritesView.as_view(), name='user-favorites'),
    
    # User listings
    path('my-listings/', views.UserListingsView.as_view(), name='user-listings'),
    
    # Reports
    path('<int:listing_id>/report/', views.ListingReportView.as_view(), name='listing-report'),
    
    # Images
    path('<int:listing_id>/images/', views.ListingImageUploadView.as_view(), name='listing-image-upload'),
    path('images/<int:pk>/delete/', views.ListingImageDeleteView.as_view(), name='listing-image-delete'),
] 