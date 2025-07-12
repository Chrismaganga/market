from django.contrib import admin
from .models import Payment, PaymentMethod, Refund, Transaction, Payout


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'seller', 'amount', 'currency', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = ['buyer__username', 'seller__username', 'listing__title', 'stripe_payment_intent_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Payment Details', {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id', 'amount', 'currency', 'payment_method')
        }),
        ('Users & Listing', {
            'fields': ('buyer', 'seller', 'listing')
        }),
        ('Status', {
            'fields': ('status', 'completed_at')
        }),
        ('Metadata', {
            'fields': ('description', 'metadata'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_method_type', 'display_name', 'is_default', 'is_active']
    list_filter = ['payment_method_type', 'is_default', 'is_active', 'created_at']
    search_fields = ['user__username', 'stripe_payment_method_id']
    ordering = ['-created_at']
    
    def display_name(self, obj):
        return str(obj)
    display_name.short_description = 'Display Name'


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['payment__id', 'stripe_refund_id', 'reason']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'processed_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'transaction_type', 'amount', 'currency', 'created_at']
    list_filter = ['transaction_type', 'currency', 'created_at']
    search_fields = ['user__username', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['id', 'seller', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['seller__username', 'stripe_payout_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'processed_at'] 