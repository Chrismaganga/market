from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from apps.listings.models import ListingReport
from .serializers import ModerationReportSerializer

class ModerationPlaceholderView(APIView):
    """Placeholder view for moderation endpoints."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response({
            'message': 'Moderation API is under development',
            'endpoints': [
                'POST /api/v1/moderation/reports/ - Report listing/user',
                'GET /api/v1/moderation/reports/ - List reports (Admin/Moderator only)',
                'PUT /api/v1/moderation/reports/{id}/ - Update report status'
            ]
        })

class ModerationReportListView(generics.ListAPIView):
    """View for listing reports (Admin/Moderator only)."""
    
    serializer_class = ModerationReportSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ListingReport.objects.all().order_by('-created_at')

class ModerationReportDetailView(generics.RetrieveAPIView):
    """View for report details and updates (Admin/Moderator only)."""
    
    serializer_class = ModerationReportSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ListingReport.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "report_id"
    
    def perform_update(self, serializer):
        serializer.save(
            reviewed_by=self.request.user,
            reviewed_at=timezone.now()
        ) 