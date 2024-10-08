from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('book/<int:flight_id>/', views.book, name='book'),
    path('get_destinations/<int:origin_id>/', views.get_destinations, name='get_destinations'),
    path('book/<int:flight_id>/<int:return_flight_id>/', views.book, name='book'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/', views.bookings, name='bookings'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('terms/', views.terms, name='terms'),
    path('ticket/<int:booking_id>/', views.ticket, name='ticket'),
    path('about/', views.about, name='about'),
    path('add-flight/', views.add_flight, name='add_flight'),
    path('booking_confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('flight/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    path('search/results/', views.search_results, name='search_results'),
    path('cancel_booking/', views.cancel_booking, name='cancel_booking'),
    path('confirm_cancel_booking/<str:passenger_id>/', views.confirm_cancel_booking, name='confirm_cancel_booking'),
]

