"""
URL configuration for marketplace project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Local Marketplace API",
        default_version='v1',
        description="API for Local Marketplace application",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@localmarketplace.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API endpoints
    path('api/v1/', include([
        path('auth/', include('apps.users.urls')),
        path('categories/', include('apps.categories.urls')),
        path('listings/', include('apps.listings.urls')),
        path('chat/', include('apps.chat.urls')),
        path('payments/', include('apps.payments.urls')),
        path('moderation/', include('apps.moderation.urls')),
    ])),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 