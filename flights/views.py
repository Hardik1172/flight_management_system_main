# flights/views.py

from .forms import SearchForm, BookingForm, PaymentForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import datetime
import logging
from .models import Flight, Airport, Booking
from .forms import SearchForm, BookingForm, CustomUserCreationForm
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import FlightForm

logger = logging.getLogger(__name__)

def index(request):
    airports = Airport.objects.all()[:5]  # Get 5 popular airports
    domestic_flights = Flight.objects.filter(is_international=False)[:5]
    international_flights = Flight.objects.filter(is_international=True)[:5]
    return render(request, 'flights/index.html', {
        'airports': airports,
        'domestic_flights': domestic_flights,
        'international_flights': international_flights
    })

@require_http_methods(["GET", "POST"])
def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            date = form.cleaned_data['date']
            passengers = form.cleaned_data['passengers']

            flights = Flight.objects.filter(
                origin=origin,
                destination=destination,
                departure_time__date=date,
                available_seats__gte=passengers

            )

            if not flights:
                messages.info(request, "No flights found matching your criteria.")

            return render(request, 'flights/search_results.html', {'flights': flights, 'form': form})
    else:
        form = SearchForm()

    return render(request, 'flights/search.html', {'form': form})




@login_required
def book(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.flight = flight
            if booking.seats <= flight.available_seats:
                booking.save()
                flight.available_seats -= booking.seats
                flight.save()
                messages.success(request, 'Booking created successfully.')
                return redirect('payment', booking_id=booking.id)
            else:
                messages.error(request, 'Not enough seats available.')
    else:
        form = BookingForm()
    return render(request, 'flights/book.html', {'form': form, 'flight': flight})

@login_required
def bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'flights/bookings.html', {'bookings': bookings})





@login_required
def add_flight(request):
    if request.method == 'POST':
        form = FlightForm(request.Post)
        if form.is_valid():
            flight = form.save(commit=False)
            flight.added_by = request.user
            flight.save()
            messages.success(request, 'Flight added successfully.')
            return redirect('index')
        else:
            messages.error(request, 'Error adding flight. Please check the form.')
    else:
        form = FlightForm()
    return render(request, 'flights/add_flight.html', {'form': form})

def contact(request):
    return render(request, 'flights/contact.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('index')
        else:
            messages.error(request, 'Registration failed. Please correct the errors.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'flights/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')


@login_required
def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.amount = booking.total_price()
            payment.save()
            booking.status = 'Paid'
            booking.save()
            messages.success(request, 'Payment successful. Your booking is confirmed.')
            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        form = PaymentForm()
    return render(request, 'flights/payment.html', {'form': form, 'booking': booking})

@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'flights/booking_confirmation.html', {'booking': booking})

def privacy_policy(request):
    return render(request, 'flights/privacy_policy.html')

def terms(request):
    return render(request, 'flights/terms.html')

@login_required
def ticket(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'flights/ticket.html', {'booking': booking})

def about(request):
    return render(request, 'flights/about.html')