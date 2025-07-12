from django.urls import path
from . import views

app_name = 'moderation'

urlpatterns = [
    path('', views.ModerationPlaceholderView.as_view(), name='moderation-home'),
    path('reports/', views.ModerationReportListView.as_view(), name='report-list'),
    path('reports/<int:report_id>/', views.ModerationReportDetailView.as_view(), name='report-detail'),
] 