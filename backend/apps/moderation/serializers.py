from rest_framework import serializers
from apps.listings.models import ListingReport

class ModerationReportSerializer(serializers.ModelSerializer):
    """Serializer for moderation reports using existing ListingReport model."""
    
    reporter_username = serializers.CharField(source='reporter.username', read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    reviewer_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    
    class Meta:
        model = ListingReport
        fields = [
            'id', 'reporter', 'reporter_username', 'listing', 'listing_title',
            'report_type', 'description', 'status', 'reviewed_by', 'reviewer_username',
            'reviewed_at', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reporter', 'reporter_username', 'listing_title',
                           'reviewer_username', 'reviewed_at', 'created_at', 'updated_at'] 