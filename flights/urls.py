from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('book/<int:flight_id>/', views.book, name='book'),
    path('bookings/', views.bookings, name='bookings'),
    path('contact/', views.contact, name='contact'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('register/', views.register, name='register'),
    path('payment/', views.payment, name='payment'),
    path('payment/process/', views.payment_process, name='payment_process'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),
    path('ticket/<int:booking_id>/', views.ticket, name='ticket'),
    path('about/', views.about, name='about'),
]