from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserVerification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_seller', 'is_active', 'created_at']
    list_filter = ['is_seller', 'is_active', 'email_verified', 'phone_verified', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('phone_number', 'bio', 'avatar', 'date_of_birth')
        }),
        ('Location', {
            'fields': ('location', 'address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Verification', {
            'fields': ('email_verified', 'phone_verified', 'is_seller')
        }),
        ('Preferences', {
            'fields': ('notification_preferences',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Profile', {
            'fields': ('phone_number', 'bio', 'avatar', 'date_of_birth')
        }),
        ('Location', {
            'fields': ('location', 'address', 'city', 'state', 'country', 'postal_code')
        }),
    )


@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'verification_type', 'status', 'created_at']
    list_filter = ['verification_type', 'status', 'created_at']
    search_fields = ['user__username', 'user__email']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'verification_type')
        }),
        ('Verification Details', {
            'fields': ('status', 'document', 'notes')
        }),
        ('Admin Actions', {
            'fields': ('verified_by', 'verified_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at'] 