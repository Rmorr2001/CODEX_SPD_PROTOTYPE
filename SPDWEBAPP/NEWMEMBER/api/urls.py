from django.urls import path
from .dashboard import NewMemberMarksView
from .commands import SubmissionView, MarkView, DecisionView, RevokeView
from .reads import OptionsView, ReviewView, HistoryView, ExportView

urlpatterns = [
    path('', NewMemberMarksView.as_view(), name='api_new_members'),
    path('submissions/', SubmissionView.as_view(), name='api_mark_submit'),
    path('options/', OptionsView.as_view(), name='api_mark_options'),
    path('review/', ReviewView.as_view(), name='api_mark_review'),
    path('history/<int:user_id>/', HistoryView.as_view(), name='api_mark_history'),
    path('export/', ExportView.as_view(), name='api_mark_export'),
    path('<int:mark_id>/', MarkView.as_view(), name='api_mark_detail'),
    path('<int:mark_id>/decision/', DecisionView.as_view(), name='api_mark_decide'),
    path('<int:mark_id>/revoke/', RevokeView.as_view(), name='api_mark_revoke'),
]
