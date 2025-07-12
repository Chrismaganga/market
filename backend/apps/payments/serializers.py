from rest_framework import serializers
from .models import Payment, PaymentMethod, Refund, Transaction, Payout
from apps.users.serializers import UserProfileSerializer
from apps.listings.serializers import ListingSerializer


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment methods."""
    
    user = UserProfileSerializer(read_only=True)
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'user', 'payment_method_type', 'display_name',
            'card_brand', 'card_last4', 'card_exp_month', 'card_exp_year',
            'bank_name', 'bank_last4', 'is_default', 'is_active',
            'created_at'
        ]
        read_only_fields = ['user', 'created_at']
    
    def get_display_name(self, obj):
        return str(obj)


class PaymentMethodCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment methods."""
    
    stripe_payment_method_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'payment_method_type', 'stripe_payment_method_id',
            'is_default'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments."""
    
    buyer = UserProfileSerializer(read_only=True)
    seller = UserProfileSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'stripe_payment_intent_id', 'stripe_charge_id',
            'amount', 'currency', 'payment_method', 'status',
            'buyer', 'seller', 'listing', 'description',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'buyer', 'seller', 'listing', 'stripe_payment_intent_id',
            'stripe_charge_id', 'status', 'created_at', 'updated_at', 'completed_at'
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments."""
    
    listing_id = serializers.IntegerField(write_only=True)
    payment_method_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Payment
        fields = ['listing_id', 'payment_method_id', 'amount', 'currency', 'description']
    
    def create(self, validated_data):
        listing_id = validated_data.pop('listing_id')
        payment_method_id = validated_data.pop('payment_method_id', None)
        
        from apps.listings.models import Listing
        listing = Listing.objects.get(id=listing_id)
        
        validated_data.update({
            'buyer': self.context['request'].user,
            'seller': listing.seller,
            'listing': listing
        })
        
        return super().create(validated_data)


class RefundSerializer(serializers.ModelSerializer):
    """Serializer for refunds."""
    
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = Refund
        fields = [
            'id', 'payment', 'stripe_refund_id', 'amount', 'currency',
            'reason', 'status', 'created_at', 'updated_at', 'processed_at'
        ]
        read_only_fields = [
            'stripe_refund_id', 'status', 'created_at', 'updated_at', 'processed_at'
        ]


class RefundCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating refunds."""
    
    payment_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Refund
        fields = ['payment_id', 'amount', 'reason']
    
    def create(self, validated_data):
        payment_id = validated_data.pop('payment_id')
        payment = Payment.objects.get(id=payment_id)
        validated_data['payment'] = payment
        return super().create(validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transactions."""
    
    user = UserProfileSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)
    refund = RefundSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'transaction_type', 'payment', 'refund',
            'amount', 'currency', 'balance_before', 'balance_after',
            'description', 'created_at'
        ]
        read_only_fields = ['user', 'balance_before', 'balance_after', 'created_at']


class PayoutSerializer(serializers.ModelSerializer):
    """Serializer for payouts."""
    
    seller = UserProfileSerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    
    class Meta:
        model = Payout
        fields = [
            'id', 'seller', 'stripe_payout_id', 'amount', 'currency',
            'status', 'payment_method', 'description', 'created_at',
            'updated_at', 'processed_at'
        ]
        read_only_fields = [
            'seller', 'stripe_payout_id', 'status', 'created_at',
            'updated_at', 'processed_at'
        ]


class PayoutCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payouts."""
    
    payment_method_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Payout
        fields = ['amount', 'currency', 'payment_method_id', 'description']
    
    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)


class StripePaymentIntentSerializer(serializers.Serializer):
    """Serializer for creating Stripe payment intents."""
    
    listing_id = serializers.IntegerField()
    payment_method_id = serializers.CharField(required=False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='USD')
    description = serializers.CharField(required=False)


class StripeSetupIntentSerializer(serializers.Serializer):
    """Serializer for creating Stripe setup intents."""
    
    payment_method_types = serializers.ListField(
        child=serializers.CharField(),
        default=['card']
    )


class PaymentConfirmationSerializer(serializers.Serializer):
    """Serializer for confirming payments."""
    
    payment_intent_id = serializers.CharField()
    payment_method_id = serializers.CharField(required=False) 