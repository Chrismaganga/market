from django.contrib import admin
from .models import Listing, ListingImage, ListingFavorite, ListingView, ListingReport


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'category', 'price', 'status', 'is_active', 'created_at']
    list_filter = ['status', 'is_active', 'is_featured', 'is_negotiable', 'condition', 'category', 'created_at']
    search_fields = ['title', 'description', 'seller__username', 'seller__email']
    ordering = ['-created_at']
    readonly_fields = ['views_count', 'favorites_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'price', 'currency')
        }),
        ('Category & Condition', {
            'fields': ('category', 'condition')
        }),
        ('Seller & Contact', {
            'fields': ('seller', 'contact_phone', 'contact_email')
        }),
        ('Location', {
            'fields': ('location', 'address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Status & Settings', {
            'fields': ('status', 'is_active', 'is_featured', 'is_negotiable')
        }),
        ('Statistics', {
            'fields': ('views_count', 'favorites_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('attributes', 'expires_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ['listing', 'is_primary', 'sort_order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['listing__title']
    ordering = ['listing', 'is_primary', 'sort_order']


@admin.register(ListingFavorite)
class ListingFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'listing__title']
    ordering = ['-created_at']


@admin.register(ListingView)
class ListingViewAdmin(admin.ModelAdmin):
    list_display = ['listing', 'user', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['listing__title', 'user__username', 'ip_address']
    ordering = ['-viewed_at']
    readonly_fields = ['viewed_at']


@admin.register(ListingReport)
class ListingReportAdmin(admin.ModelAdmin):
    list_display = ['listing', 'reporter', 'report_type', 'status', 'created_at']
    list_filter = ['report_type', 'status', 'created_at']
    search_fields = ['listing__title', 'reporter__username', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('listing', 'reporter', 'report_type', 'description')
        }),
        ('Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'notes')
        }),
    ) 