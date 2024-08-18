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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Flight, Airport, Booking, Stopover
from .forms import SearchForm, BookingForm, FlightForm, PaymentForm, CustomUserCreationForm, StopoverInlineFormSet , PassengerForm
from django.contrib.auth import login, authenticate, logout
from django.forms import formset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Flight, Booking, Passenger
from .forms import BookingForm, PassengerFormSet

logger = logging.getLogger(__name__)


def index(request):
    airports = Airport.objects.all()[:5]
    domestic_flights = Flight.objects.filter(is_international=False)[:5]
    international_flights = Flight.objects.filter(is_international=True)[:5]
    search_form = SearchForm()
    return render(request, 'flights/index.html', {
        'airports': airports,
        'domestic_flights': domestic_flights,
        'international_flights': international_flights,
        'search_form': search_form
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

            # Store passenger counts in session
            request.session['adults'] = adults
            request.session['children'] = children
            request.session['infants'] = infants

            outbound_flights = Flight.objects.filter(
                origin=origin,
                destination=destination,
                departure_time__date=departure_date,
                available_seats__gte=total_passengers
            ).prefetch_related('stopovers')

            return_flights = None
            if trip_type == 'round_trip' and return_date:
                return_flights = Flight.objects.filter(
                    origin=destination,
                    destination=origin,
                    departure_time__date=return_date,
                    available_seats__gte=total_passengers
                ).prefetch_related('stopovers')

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

    adults = int(request.session.get('adults', 0))
    children = int(request.session.get('children', 0))
    infants = int(request.session.get('infants', 0))
    total_passengers = adults + children + infants

    if request.method == 'POST':
        booking_form = BookingForm(request.POST)
        passengers_data = []
        for i in range(total_passengers):
            prefix = f'passenger_{i}'
            passenger_form = PassengerForm(request.POST, prefix=prefix)
            if passenger_form.is_valid():
                passengers_data.append(passenger_form)
            else:
                messages.error(request, f'Error in passenger {i+1} details. Please check and try again.')
                break

        if booking_form.is_valid() and len(passengers_data) == total_passengers:
            booking = booking_form.save(commit=False)
            booking.user = request.user
            booking.flight = flight
            booking.return_flight = return_flight
            booking.adults = adults
            booking.children = children
            booking.infants = infants
            booking.save()

            for passenger_form in passengers_data:
                passenger = passenger_form.save(commit=False)
                passenger.booking = booking
                passenger.save()

            messages.success(request, 'Booking created successfully.')
            return redirect('payment', booking_id=booking.id)
    else:
        booking_form = BookingForm()

    context = {
        'booking_form': booking_form,
        'flight': flight,
        'return_flight': return_flight,
        'adults': adults,
        'children': children,
        'infants': infants,
        'total_passengers': total_passengers,
    }
    return render(request, 'flights/book.html', context)



@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    passengers = booking.passengers.all()
    context = {
        'booking': booking,
        'passengers': passengers,
    }
    return render(request, 'flights/booking_detail.html', context)

@login_required
def bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('flight')
    context = {
        'bookings': bookings
    }
    return render(request, 'flights/bookings.html', context)



@login_required
def payment(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.amount = booking.total_price()
            payment.save()
            messages.success(request, 'Payment successful. Your booking is confirmed.')
            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        form = PaymentForm()

    context = {
        'form': form,
        'booking': booking,
        'total_price': booking.total_price(),
    }
    return render(request, 'flights/payment.html', context)


@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    return render(request, 'flights/booking_confirmation.html', {'booking': booking})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("index")
    else:
        form = CustomUserCreationForm()
    return render(request, "flights/register.html", {"form": form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully logged in.")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'flights/login.html')


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('index')


@login_required
def add_flight(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
        stopover_formset = StopoverInlineFormSet(request.POST)
        if form.is_valid() and stopover_formset.is_valid():
            flight = form.save()
            stopover_formset.instance = flight
            stopover_formset.save()
            messages.success(request, 'Flight added successfully.')
            return redirect('index')
    else:
        form = FlightForm()
        stopover_formset = StopoverInlineFormSet()

    context = {
        'form': form,
        'stopover_formset': stopover_formset,
    }
    return render(request, 'flights/add_flight.html', context)


def flight_detail(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)
    stopovers = flight.stopovers.all().order_by('arrival_time')
    context = {
        'flight': flight,
        'stopovers': stopovers,
    }
    return render(request, 'flights/flight_detail.html', context)

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
def contact(request):
    return render(request, 'flights/contact.html')