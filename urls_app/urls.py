from django.urls import path
from .views import ShortenURLView, URLDetailView, URLStatsView

urlpatterns = [
    path('shorten', ShortenURLView.as_view(), name='url-shorten'),
    path('shorten/<str:short_code>', URLDetailView.as_view(), name='url-detail'),
    path('shorten/<str:short_code>/stats', URLStatsView.as_view(), name='url-stats'),
]
