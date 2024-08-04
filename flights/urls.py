from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_flights, name='search_flights'),
    path('book/<int:flight_id>/', views.book_flight, name='book_flight'),
    path('payment/<str:booking_ids>/', views.payment, name='payment'),
    path('confirmation/<str:booking_ids>/', views.booking_confirmation, name='booking_confirmation'),
    path('bookings/', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
]