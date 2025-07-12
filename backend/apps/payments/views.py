from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
import stripe

from .models import Payment, PaymentMethod, Refund, Transaction, Payout
from .serializers import (
    PaymentSerializer, PaymentCreateSerializer, PaymentMethodSerializer,
    PaymentMethodCreateSerializer, RefundSerializer, RefundCreateSerializer,
    TransactionSerializer, PayoutSerializer, PayoutCreateSerializer,
    StripePaymentIntentSerializer, StripeSetupIntentSerializer,
    PaymentConfirmationSerializer
)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentMethodListView(generics.ListAPIView):
    """View for listing user's payment methods."""
    
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(
            user=self.request.user,
            is_active=True
        )


class PaymentMethodCreateView(generics.CreateAPIView):
    """View for creating payment methods."""
    
    serializer_class = PaymentMethodCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        stripe_payment_method_id = serializer.validated_data['stripe_payment_method_id']
        
        try:
            # Retrieve payment method from Stripe
            payment_method = stripe.PaymentMethod.retrieve(stripe_payment_method_id)
            
            # Create local payment method
            payment_method_obj = serializer.save()
            
            # Update with Stripe data
            if payment_method.type == 'card':
                payment_method_obj.card_brand = payment_method.card.brand
                payment_method_obj.card_last4 = payment_method.card.last4
                payment_method_obj.card_exp_month = payment_method.card.exp_month
                payment_method_obj.card_exp_year = payment_method.card.exp_year
            elif payment_method.type == 'bank_account':
                payment_method_obj.bank_name = payment_method.bank_account.bank_name
                payment_method_obj.bank_last4 = payment_method.bank_account.last4
                payment_method_obj.bank_routing_number = payment_method.bank_account.routing_number
            
            payment_method_obj.stripe_payment_method_id = stripe_payment_method_id
            payment_method_obj.save()
            
        except stripe.error.StripeError as e:
            raise serializers.ValidationError(f"Stripe error: {str(e)}")


class PaymentMethodDeleteView(generics.DestroyAPIView):
    """View for deleting payment methods."""
    
    permission_classes = [permissions.IsAuthenticated]
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "payment_method_id"
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)


class PaymentListView(generics.ListAPIView):
    """View for listing user's payments."""
    
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(
            buyer=user
        ).select_related('seller', 'listing')


class PaymentDetailView(generics.RetrieveAPIView):
    """View for payment details."""
    
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "payment_id"
    
    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(
            buyer=user
        ).select_related('seller', 'listing')


class PaymentCreateView(generics.CreateAPIView):
    """View for creating payments."""
    
    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        payment = serializer.save()
        
        # Create transaction record
        Transaction.objects.create(
            user=payment.buyer,
            transaction_type='payment',
            payment=payment,
            amount=payment.amount,
            currency=payment.currency,
            balance_before=0,  # TODO: Calculate actual balance
            balance_after=0,   # TODO: Calculate actual balance
            description=f"Payment for {payment.listing.title}"
        )


class RefundListView(generics.ListAPIView):
    """View for listing refunds."""
    
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Refund.objects.filter(
            payment__buyer=user
        ).select_related('payment')


class RefundCreateView(generics.CreateAPIView):
    """View for creating refunds."""
    
    serializer_class = RefundCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        refund = serializer.save()
        
        # Create transaction record
        Transaction.objects.create(
            user=refund.payment.buyer,
            transaction_type='refund',
            refund=refund,
            amount=refund.amount,
            currency=refund.currency,
            balance_before=0,  # TODO: Calculate actual balance
            balance_after=0,   # TODO: Calculate actual balance
            description=f"Refund for payment {refund.payment.id}"
        )


class TransactionListView(generics.ListAPIView):
    """View for listing user's transactions."""
    
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user
        ).select_related('payment', 'refund')


class PayoutListView(generics.ListAPIView):
    """View for listing seller's payouts."""
    
    serializer_class = PayoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payout.objects.filter(
            seller=self.request.user
        ).select_related('payment_method')


class PayoutCreateView(generics.CreateAPIView):
    """View for creating payouts."""
    
    serializer_class = PayoutCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        payout = serializer.save()
        
        # Create transaction record
        Transaction.objects.create(
            user=payout.seller,
            transaction_type='transfer',
            amount=payout.amount,
            currency=payout.currency,
            balance_before=0,  # TODO: Calculate actual balance
            balance_after=0,   # TODO: Calculate actual balance
            description=f"Payout of {payout.amount} {payout.currency}"
        )


class StripePaymentIntentView(APIView):
    """View for creating Stripe payment intents."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = StripePaymentIntentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                listing_id = serializer.validated_data['listing_id']
                amount = serializer.validated_data['amount']
                currency = serializer.validated_data['currency']
                description = serializer.validated_data.get('description', '')
                
                # Get listing
                from apps.listings.models import Listing
                listing = get_object_or_404(Listing, id=listing_id)
                
                # Create payment intent
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(amount * 100),  # Convert to cents
                    currency=currency.lower(),
                    description=description or f"Payment for {listing.title}",
                    metadata={
                        'listing_id': listing_id,
                        'buyer_id': request.user.id,
                        'seller_id': listing.seller.id
                    }
                )
                
                return Response({
                    'client_secret': payment_intent.client_secret,
                    'payment_intent_id': payment_intent.id
                })
                
            except stripe.error.StripeError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StripeSetupIntentView(APIView):
    """View for creating Stripe setup intents."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = StripeSetupIntentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                setup_intent = stripe.SetupIntent.create(
                    payment_method_types=serializer.validated_data['payment_method_types'],
                    customer=request.user.stripe_customer_id if hasattr(request.user, 'stripe_customer_id') else None
                )
                
                return Response({
                    'client_secret': setup_intent.client_secret,
                    'setup_intent_id': setup_intent.id
                })
                
            except stripe.error.StripeError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_payment(request):
    """Confirm a payment with Stripe."""
    serializer = PaymentConfirmationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            payment_intent_id = serializer.validated_data['payment_intent_id']
            
            # Confirm the payment intent
            payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)
            
            if payment_intent.status == 'succeeded':
                # Update local payment record
                payment = get_object_or_404(
                    Payment,
                    stripe_payment_intent_id=payment_intent_id
                )
                payment.status = 'completed'
                payment.stripe_charge_id = payment_intent.latest_charge
                payment.save()
                
                return Response({'status': 'success'})
            else:
                return Response(
                    {'error': f'Payment failed: {payment_intent.status}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_methods_summary(request):
    """Get summary of user's payment methods."""
    payment_methods = PaymentMethod.objects.filter(
        user=request.user,
        is_active=True
    )
    
    summary = {
        'total_methods': payment_methods.count(),
        'default_method': None,
        'card_methods': payment_methods.filter(payment_method_type='card').count(),
        'bank_methods': payment_methods.filter(payment_method_type='bank_account').count(),
    }
    
    default_method = payment_methods.filter(is_default=True).first()
    if default_method:
        summary['default_method'] = {
            'id': default_method.id,
            'type': default_method.payment_method_type,
            'display_name': str(default_method)
        }
    
    return Response(summary) 