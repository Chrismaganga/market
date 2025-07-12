from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    
    # Profile management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserUpdateView.as_view(), name='profile-update'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    
    # Verification
    path('verification/', views.UserVerificationView.as_view(), name='verification-create'),
    path('verification/list/', views.UserVerificationListView.as_view(), name='verification-list'),
    
    # Admin verification management
    path('admin/verification/list/', views.AdminUserVerificationListView.as_view(), name='admin-verification-list'),
    path('admin/verification/<int:pk>/update/', views.AdminUserVerificationUpdateView.as_view(), name='admin-verification-update'),
] 