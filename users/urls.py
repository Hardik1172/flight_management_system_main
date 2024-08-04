from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    # Add other user-related URL patterns
]