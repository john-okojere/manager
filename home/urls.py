from django.urls import path
from . import views

urlpatterns = [
    path('', views.combined_dashboard, name='home'),
    # Add more paths here as needed
]