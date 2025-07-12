from django.urls import path
from . import views, webhooks

app_name = 'payments'

urlpatterns = [
    # Payment methods
    path('methods/', views.PaymentMethodListView.as_view(), name='payment-method-list'),
    path('methods/create/', views.PaymentMethodCreateView.as_view(), name='payment-method-create'),
    path('methods/<int:pk>/delete/', views.PaymentMethodDeleteView.as_view(), name='payment-method-delete'),
    path('methods/summary/', views.payment_methods_summary, name='payment-methods-summary'),
    
    # Payments
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('create/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    
    # Refunds
    path('refunds/', views.RefundListView.as_view(), name='refund-list'),
    path('refunds/create/', views.RefundCreateView.as_view(), name='refund-create'),
    
    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    
    # Payouts
    path('payouts/', views.PayoutListView.as_view(), name='payout-list'),
    path('payouts/create/', views.PayoutCreateView.as_view(), name='payout-create'),
    
    # Stripe integration
    path('stripe/payment-intent/', views.StripePaymentIntentView.as_view(), name='stripe-payment-intent'),
    path('stripe/setup-intent/', views.StripeSetupIntentView.as_view(), name='stripe-setup-intent'),
    path('stripe/confirm-payment/', views.confirm_payment, name='stripe-confirm-payment'),
    path('stripe/webhook/', webhooks.stripe_webhook, name='stripe-webhook'),
] 