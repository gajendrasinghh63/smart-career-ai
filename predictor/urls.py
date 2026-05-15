
from django.urls import path
from . import views
from .api_views import predict_api

urlpatterns = [
    path('', views.home_view, name='home'),

    # API
    path('api/predict/', predict_api, name='predict_api'),

    # PDF
    path('download/<int:id>/', views.download_pdf, name='download_pdf'),

    # Clear history
    path('clear-history/', views.clear_history, name='clear_history'),
]