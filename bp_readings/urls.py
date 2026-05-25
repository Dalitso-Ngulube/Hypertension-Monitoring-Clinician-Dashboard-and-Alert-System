from django.urls import path
from .views import BPReadingListCreateView, BPReadingDetailView

urlpatterns = [
    path('', BPReadingListCreateView.as_view(), name='bp-reading-list-create'),
    path('<int:pk>/', BPReadingDetailView.as_view(), name='bp-reading-detail'),
]