from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('book/<int:flight_id>/', views.book, name='book'),
    path('book/<int:flight_id>/<int:return_flight_id>/', views.book, name='book'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/', views.bookings, name='bookings'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),
    path('ticket/<int:booking_id>/', views.ticket, name='ticket'),
    path('about/', views.about, name='about'),
    path('add_flight/', views.add_flight, name='add_flight'),
    path('booking_confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('flight/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    path('search/results/', views.search_results, name='search_results'),
    path('book/<int:outbound_flight_id>/<int:return_flight_id>/', views.book, name='book')
]