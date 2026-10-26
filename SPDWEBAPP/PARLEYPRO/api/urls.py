"""JSON poll endpoints, separate from the legacy HTML /poll/ routes."""
from django.urls import path
from .commands import PollCollectionView, PollDetailView, BallotView, CloseView

urlpatterns = [
    path('', PollCollectionView.as_view(), name='api_decisions'),
    path('<int:poll_id>/', PollDetailView.as_view(), name='api_poll_detail'),
    path('<int:poll_id>/vote/', BallotView.as_view(), name='api_poll_vote'),
    path('<int:poll_id>/close/', CloseView.as_view(), name='api_poll_close'),
]
