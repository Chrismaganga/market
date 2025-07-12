"""
URL configuration for marketplace project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import get_resolver
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator

# Schema view configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Local Marketplace API",
        default_version='v1',
        description="API for Local Marketplace application",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Add a comprehensive API documentation homepage
def homepage(request):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Local Marketplace API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #34495e;
                border-left: 4px solid #3498db;
                padding-left: 15px;
                margin-top: 30px;
            }
            .endpoint {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                padding: 15px;
                margin: 10px 0;
                font-family: 'Courier New', monospace;
            }
            .method {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 3px;
                font-weight: bold;
                margin-right: 10px;
                font-size: 12px;
            }
            .get { background: #d4edda; color: #155724; }
            .post { background: #d1ecf1; color: #0c5460; }
            .put { background: #fff3cd; color: #856404; }
            .delete { background: #f8d7da; color: #721c24; }
            .patch { background: #e2e3e5; color: #383d41; }
            .description {
                color: #6c757d;
                font-style: italic;
                margin-top: 5px;
            }
            .links {
                margin-top: 30px;
                text-align: center;
            }
            .links a {
                display: inline-block;
                margin: 0 10px;
                padding: 10px 20px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background 0.3s;
            }
            .links a:hover {
                background: #2980b9;
            }
            .status {
                background: #28a745;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 12px;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏪 Local Marketplace API</h1>
            <p style="text-align: center; color: #6c757d; font-size: 18px;">
                Welcome to the Local Marketplace Backend API Documentation
            </p>
            
            <h2>📚 API Documentation</h2>
            <div class="links">
                <a href="/api/docs/" target="_blank">📖 Swagger UI</a>
                <a href="/api/redoc/" target="_blank">📋 ReDoc</a>
                <a href="/admin/" target="_blank">⚙️ Admin Panel</a>
            </div>

            <h2>🔐 Authentication</h2>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/v1/auth/login/</code>
                <span class="description">User login with email/password</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/v1/auth/register/</code>
                <span class="description">User registration</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/v1/auth/refresh/</code>
                <span class="description">Refresh JWT token</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/v1/auth/logout/</code>
                <span class="description">User logout</span>
            </div>

            <h2>👥 Users</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/v1/auth/profile/</code>
                <span class="description">Get current user profile</span>
            </div>
            <div class="endpoint">
                <span class="method put">PUT</span>
                <code>/api/v1/auth/profile/</code>
                <span class="description">Update user profile</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/v1/auth/change-password/</code>
                <span class="description">Change user password</span>
            </div>

            <h2>📂 Categories</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/v1/categories/</code>
                <span class="description">List all categories</span>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/v1/categories/{id}/</code>
                <span class="description">Get category details</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/v1/categories/</code>
                <span class="description">Create new category (Admin only)</span>
            </div>

            <h2>🏷️ Listings</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/v1/listings/</code>
                <span class="description">List all listings with filters</span>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/v1/listings/{id}/</code>
                <span class="description">Get listing details</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/v1/listings/</code>
                <span class="description">Create new listing</span>
            </div>
            <div class="endpoint">
                <span class="method put">PUT</span>
                <code>/api/v1/listings/{id}/</code>
                <span class="description">Update listing</span>
            </div>
            <div class="endpoint">
                <span class="method delete">DELETE</span>
                <code>/api/v1/listings/{id}/</code>
                <span class="description">Delete listing</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/v1/listings/{id}/favorite/</code>
                <span class="description">Add/remove from favorites</span>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/v1/listings/my-listings/</code>
                <span class="description">Get user's own listings</span>
            </div>

            <h2>💬 Chat</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/v1/chat/rooms/</code>
                <span class="description">List user's chat rooms</span>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/v1/chat/rooms/{id}/</code>
                <span class="description">Get chat room details</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/v1/chat/rooms/</code>
                <span class="description">Create new chat room</span>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/v1/chat/rooms/{id}/messages/</code>
                <span class="description">Get chat messages</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/v1/chat/rooms/{id}/messages/</code>
                <span class="description">Send message</span>
            </div>

            <h2>💳 Payments</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/v1/payments/methods/</code>
                <span class="description">List payment methods</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/v1/payments/methods/</code>
                <span class="description">Add payment method</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/v1/payments/process/</code>
                <span class="description">Process payment</span>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/v1/payments/transactions/</code>
                <span class="description">List transactions</span>
            </div>

            <h2>🛡️ Moderation</h2>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/v1/moderation/reports/</code>
                <span class="description">Report listing/user</span>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/v1/moderation/reports/</code>
                <span class="description">List reports (Admin/Moderator only)</span>
            </div>
            <div class="endpoint">
                <span class="method put">PUT</span>
                <code>/api/v1/moderation/reports/{id}/</code>
                <span class="description">Update report status</span>
            </div>

            <h2>🔧 System Status</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/__debug__/</code>
                <span class="description">Django Debug Toolbar (Development only)</span>
            </div>

            <div style="margin-top: 40px; text-align: center; color: #6c757d;">
                <p><strong>API Base URL:</strong> <code>http://127.0.0.1:8000/api/v1/</code></p>
                <p><strong>Authentication:</strong> JWT Bearer Token</p>
                <p><strong>Content-Type:</strong> application/json</p>
                <span class="status">🟢 API is running</span>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content, content_type='text/html')

# API documentation
def api_docs_placeholder(request):
    return HttpResponse("""
    <html>
    <head><title>API Documentation</title></head>
    <body>
        <h1>API Documentation</h1>
        <p>Swagger UI is temporarily unavailable due to schema generation issues.</p>
        <p>Please refer to the <a href="/">homepage</a> for API endpoint documentation.</p>
    </body>
    </html>
    """)

def api_redoc_placeholder(request):
    return HttpResponse("""
    <html>
    <head><title>API Documentation</title></head>
    <body>
        <h1>API Documentation</h1>
        <p>ReDoc is temporarily unavailable due to schema generation issues.</p>
        <p>Please refer to the <a href="/">homepage</a> for API endpoint documentation.</p>
    </body>
    </html>
    """)

urlpatterns = [
    path('', homepage),
    path('admin/', admin.site.urls),
    
    # API documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # API endpoints
    path('api/v1/', include([
        path('auth/', include('apps.users.urls')),
        path('categories/', include('apps.categories.urls')),
        # path('listings/', include('apps.listings.urls')),
        # path('chat/', include('apps.chat.urls')),
        # path('payments/', include('apps.payments.urls')),
        # path('moderation/', include('apps.moderation.urls')),
    ])),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns 