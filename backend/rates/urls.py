from django.urls import path
from .views import HealthView, CurrencyListView, LatestRatesView

urlpatterns = [
    path('health/', HealthView.as_view()),
    path('currencies/', CurrencyListView.as_view()),
    path('rates/', LatestRatesView.as_view()),
]
