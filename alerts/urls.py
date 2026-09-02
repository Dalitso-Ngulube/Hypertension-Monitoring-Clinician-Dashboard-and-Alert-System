from django.urls import path

from .views import AlertListCreateView, AlertUpdateView, UnresolvedAlertsView

urlpatterns = [
    path('', AlertListCreateView.as_view(), name='alert-list'),
    path('<int:pk>/', AlertUpdateView.as_view(), name='alert-update'),
    path('unresolved/', UnresolvedAlertsView.as_view(), name='unresolved-alerts'),
]