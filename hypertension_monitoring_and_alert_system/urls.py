from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

def home(request):
    return JsonResponse({"message": "Hypertension Monitoring API"})

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/patients/', include('patients.urls')),
    path('api/readings/', include('bp_readings.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/alerts/', include('alerts.urls')),
    path('api/auth/', include('accounts.urls')),
    path('api/auth/token/', TokenObtainPairView.as_view(), ),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), ),
]