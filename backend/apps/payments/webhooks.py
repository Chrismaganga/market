import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
import json

from .models import Payment, PaymentMethod, Refund, Payout


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        handle_payment_intent_succeeded(event['data']['object'])
    elif event['type'] == 'payment_intent.payment_failed':
        handle_payment_intent_failed(event['data']['object'])
    elif event['type'] == 'payment_method.attached':
        handle_payment_method_attached(event['data']['object'])
    elif event['type'] == 'payment_method.detached':
        handle_payment_method_detached(event['data']['object'])
    elif event['type'] == 'charge.refunded':
        handle_charge_refunded(event['data']['object'])
    elif event['type'] == 'payout.paid':
        handle_payout_paid(event['data']['object'])
    elif event['type'] == 'payout.failed':
        handle_payout_failed(event['data']['object'])
    else:
        # Unexpected event type
        pass
    
    return HttpResponse(status=200)


def handle_payment_intent_succeeded(payment_intent):
    """Handle successful payment intent."""
    try:
        payment = Payment.objects.get(
            stripe_payment_intent_id=payment_intent['id']
        )
        payment.status = 'completed'
        payment.stripe_charge_id = payment_intent['latest_charge']
        payment.completed_at = timezone.now()
        payment.save()
        
        # Update listing status if needed
        listing = payment.listing
        listing.status = 'sold'
        listing.save()
        
    except Payment.DoesNotExist:
        # Create new payment record if it doesn't exist
        from apps.listings.models import Listing
        from apps.users.models import User
        
        listing = Listing.objects.get(id=payment_intent['metadata']['listing_id'])
        buyer = User.objects.get(id=payment_intent['metadata']['buyer_id'])
        seller = User.objects.get(id=payment_intent['metadata']['seller_id'])
        
        Payment.objects.create(
            stripe_payment_intent_id=payment_intent['id'],
            stripe_charge_id=payment_intent['latest_charge'],
            amount=payment_intent['amount'] / 100,  # Convert from cents
            currency=payment_intent['currency'].upper(),
            status='completed',
            buyer=buyer,
            seller=seller,
            listing=listing,
            completed_at=timezone.now()
        )


def handle_payment_intent_failed(payment_intent):
    """Handle failed payment intent."""
    try:
        payment = Payment.objects.get(
            stripe_payment_intent_id=payment_intent['id']
        )
        payment.status = 'failed'
        payment.save()
    except Payment.DoesNotExist:
        pass


def handle_payment_method_attached(payment_method):
    """Handle payment method attachment."""
    # This could be used to sync payment methods
    pass


def handle_payment_method_detached(payment_method):
    """Handle payment method detachment."""
    try:
        payment_method_obj = PaymentMethod.objects.get(
            stripe_payment_method_id=payment_method['id']
        )
        payment_method_obj.is_active = False
        payment_method_obj.save()
    except PaymentMethod.DoesNotExist:
        pass


def handle_charge_refunded(charge):
    """Handle charge refund."""
    try:
        payment = Payment.objects.get(stripe_charge_id=charge['id'])
        
        # Create refund record
        Refund.objects.create(
            payment=payment,
            stripe_refund_id=charge['refunds']['data'][0]['id'],
            amount=charge['refunds']['data'][0]['amount'] / 100,
            currency=charge['currency'].upper(),
            status='succeeded',
            processed_at=timezone.now()
        )
        
        # Update payment status
        payment.status = 'refunded'
        payment.save()
        
    except Payment.DoesNotExist:
        pass


def handle_payout_paid(payout):
    """Handle successful payout."""
    try:
        payout_obj = Payout.objects.get(stripe_payout_id=payout['id'])
        payout_obj.status = 'completed'
        payout_obj.processed_at = timezone.now()
        payout_obj.save()
    except Payout.DoesNotExist:
        pass


def handle_payout_failed(payout):
    """Handle failed payout."""
    try:
        payout_obj = Payout.objects.get(stripe_payout_id=payout['id'])
        payout_obj.status = 'failed'
        payout_obj.save()
    except Payout.DoesNotExist:
        pass 