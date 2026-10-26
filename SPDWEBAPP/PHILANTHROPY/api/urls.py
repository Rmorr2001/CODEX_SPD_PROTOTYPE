"""JSON service routes; HTML /philanthropy/ routes remain independently addressable."""
from django.urls import path
from .commands import ServiceCollectionView, EventView, DecisionView, ReviewView
from .reports import ChapterView, HistoryView, OwnHistoryView, ExportView

urlpatterns = [
    path('', ServiceCollectionView.as_view(), name='api_service'),
    path('review/', ReviewView.as_view(), name='api_service_review'),
    path('chapter/', ChapterView.as_view(), name='api_service_chapter'),
    path('history/', OwnHistoryView.as_view(), name='api_service_own_history'),
    path('history/<int:user_id>/', HistoryView.as_view(), name='api_service_history'),
    path('export/', ExportView.as_view(), name='api_service_export'),
    path('<int:event_id>/', EventView.as_view(), name='api_service_event'),
    path('<int:event_id>/decision/', DecisionView.as_view(), name='api_service_decision'),
]
