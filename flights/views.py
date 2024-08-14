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
from datetime import timedelta
from django.shortcuts import render
from .forms import SearchForm
from .models import Flight
from django.contrib import messages
from datetime import timedelta

logger = logging.getLogger(__name__)

def index(request):
    airports = Airport.objects.all()[:5]
    domestic_flights = Flight.objects.filter(is_international=False)[:5]
    international_flights = Flight.objects.filter(is_international=True)[:5]
    return render(request, 'flights/index.html', {
        'airports': airports,
        'domestic_flights': domestic_flights,
        'international_flights': international_flights
    })


def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            departure_date = form.cleaned_data['departure_date']
            return_date = form.cleaned_data.get('return_date')
            adults = form.cleaned_data['adults']
            children = form.cleaned_data['children']
            infants = form.cleaned_data['infants']
            trip_type = form.cleaned_data['trip_type']

            total_passengers = adults + children + infants

            outbound_flights = Flight.objects.filter(
                origin=origin,
                destination=destination,
                departure_time__date=departure_date,
                available_seats__gte=total_passengers
            )

            return_flights = None
            if trip_type == 'round_trip' and return_date:
                return_flights = Flight.objects.filter(
                    origin=destination,
                    destination=origin,
                    departure_time__date=return_date,
                    available_seats__gte=total_passengers
                )

            if not outbound_flights:
                messages.info(request, "No outbound flights found matching your criteria.")
            elif trip_type == 'round_trip' and not return_flights:
                messages.info(request, "No return flights found on the specified date.")

            context = {
                'form': form,
                'outbound_flights': outbound_flights,
                'return_flights': return_flights,
                'adults': adults,
                'children': children,
                'infants': infants,
                'trip_type': trip_type
            }

            return render(request, 'flights/search_results.html', context)
    else:
        form = SearchForm()

    return render(request, 'flights/search.html', {'form': form})


@login_required
def book(request, flight_id, return_flight_id=None):
    flight = get_object_or_404(Flight, pk=flight_id)
    return_flight = None
    if return_flight_id:
        return_flight = get_object_or_404(Flight, pk=return_flight_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.flight = flight
            if return_flight:
                booking.return_flight = return_flight


            total_passengers = booking.adults + booking.children + booking.infants

            if total_passengers <= flight.available_seats and (
                    not return_flight or total_passengers <= return_flight.available_seats):
                booking.save()
                flight.available_seats -= total_passengers
                flight.save()
                if return_flight:
                    return_flight.available_seats -= total_passengers
                    return_flight.save()
                messages.success(request, 'Booking created successfully.')
                return redirect('payment', booking_id=booking.id)
            else:
                messages.error(request, 'Not enough seats available.')
    else:
        form = BookingForm()

    context = {
        'form': form,
        'flight': flight,
        'return_flight': return_flight
    }
    return render(request, 'flights/book.html', context)


@login_required
def bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'flights/bookings.html', {'bookings': bookings})




@login_required
def add_flight(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
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

def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            departure_date = form.cleaned_data['departure_date']
            return_date = form.cleaned_data.get('return_date')
            adults = form.cleaned_data['adults']
            children = form.cleaned_data['children']
            infants = form.cleaned_data['infants']
            trip_type = form.cleaned_data['trip_type']

            total_passengers = adults + children + infants

            outbound_flights = Flight.objects.filter(
                origin=origin,
                destination=destination,
                departure_time__date=departure_date,
                available_seats__gte=total_passengers
            )

            return_flights = None
            if trip_type == 'round_trip' and return_date:
                return_flights = Flight.objects.filter(
                    origin=destination,
                    destination=origin,
                    departure_time__date=return_date,
                    available_seats__gte=total_passengers
                )

            if not outbound_flights:
                messages.info(request, "No outbound flights found matching your criteria.")
            elif trip_type == 'round_trip' and not return_flights:
                messages.info(request, "No return flights found on the specified date.")

            context = {
                'form': form,
                'outbound_flights': outbound_flights,
                'return_flights': return_flights,
                'adults': adults,
                'children': children,
                'infants': infants,
                'trip_type': trip_type
            }

            return render(request, 'flights/search_results.html', context)
    else:
        form = SearchForm()

    return render(request, 'flights/search.html', {'form': form})


@login_required
def book(request, flight_id, return_flight_id=None):
    flight = get_object_or_404(Flight, pk=flight_id)
    return_flight = None
    if return_flight_id:
        return_flight = get_object_or_404(Flight, pk=return_flight_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.flight = flight
            if return_flight:
                booking.return_flight = return_flight

            total_passengers = booking.adults + booking.children + booking.infants

            if total_passengers <= flight.available_seats and (
                    not return_flight or total_passengers <= return_flight.available_seats):
                booking.save()
                flight.available_seats -= total_passengers
                flight.save()
                if return_flight:
                    return_flight.available_seats -= total_passengers
                    return_flight.save()
                messages.success(request, 'Booking created successfully.')
                return redirect('payment', booking_id=booking.id)
            else:
                messages.error(request, 'Not enough seats available.')
    else:
        form = BookingForm()

    context = {
        'form': form,
        'flight': flight,
        'return_flight': return_flight
    }
    return render(request, 'flights/book.html', context)


@login_required
def bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'flights/bookings.html', {'bookings': bookings})


@login_required
def add_flight(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
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
            payment.amount = booking.total_price()  # Call the method here
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