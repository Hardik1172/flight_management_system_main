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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.db.models import Q
from datetime import datetime, timedelta
import logging
from .models import Flight, Airport, Booking, Stopover, Passenger
from .forms import SearchForm, BookingForm, FlightForm, PaymentForm, CustomUserCreationForm, StopoverInlineFormSet, PassengerForm
import random
from django.shortcuts import render, redirect
from .models import SearchHistory
from .forms import SearchForm


logger = logging.getLogger(__name__)


def index(request):
    airports = Airport.objects.all()[:5]
    domestic_flights = Flight.objects.filter(is_international=False)[:5]
    international_flights = Flight.objects.filter(is_international=True)[:5]
    search_form = SearchForm()

    # Retrieve search history
    search_history = SearchHistory.objects.filter(user=request.user).order_by('-search_date')[
                     :5] if request.user.is_authenticated else []

    return render(request, 'flights/index.html', {
        'airports': airports,
        'domestic_flights': domestic_flights,
        'international_flights': international_flights,
        'search_form': search_form,
        'search_history': search_history
    })


def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            # Save the search history
            SearchHistory.objects.create(
                user=request.user if request.user.is_authenticated else None,
                origin=form.cleaned_data['origin'],
                destination=form.cleaned_data['destination'],
                departure_date=form.cleaned_data['departure_date'],
                return_date=form.cleaned_data['return_date'],
                adults=form.cleaned_data['adults'],
                children=form.cleaned_data['children'],
                infants=form.cleaned_data['infants']
            )

            # Store search parameters in session
            search_params = form.cleaned_data.copy()
            search_params['origin'] = search_params['origin'].id
            search_params['destination'] = search_params['destination'].id

            # Convert date objects to strings
            search_params['departure_date'] = search_params['departure_date'].isoformat()
            if search_params['return_date']:
                search_params['return_date'] = search_params['return_date'].isoformat()

            request.session['search_params'] = search_params


            # Redirect to search results
            return redirect('search_results')
    else:
        form = SearchForm()

    # Retrieve search history
    search_history = SearchHistory.objects.filter(user=request.user).order_by('-search_date')[
                     :5] if request.user.is_authenticated else []

    context = {
        'form': form,
        'search_history': search_history
    }
    return render(request, 'flights/search.html', context)

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
        passenger_data = {
            'adult': request.POST.getlist('passenger-adult-first_name'),
            'child': request.POST.getlist('passenger-child-first_name'),
            'infant': request.POST.getlist('passenger-infant-first_name'),
        }



        if booking_form.is_valid():
            booking = booking_form.save(commit= False)
            booking.user = request.user
            booking.flight = flight
            booking.return_flight = return_flight
            booking.adults = adults
            booking.children = children
            booking.infants = infants
            booking.save()




            for passenger_type, first_names in passenger_data.items():
                for i, first_name in enumerate(first_names):
                    last_name = request.POST.getlist(f'passenger-{passenger_type}-last_name')[i]
                    meal_choice = request.POST.getlist(f'passenger-{passenger_type}-meal_choice')[i]
                    ticket_class = request.POST.getlist(f'passenger-{passenger_type}-ticket_class')[i]
                    passenger = Passenger.objects.create(
                        booking=booking,
                        first_name=first_name,
                        last_name=last_name,
                        passenger_type=passenger_type,
                        meal_choice=meal_choice,
                        ticket_class=ticket_class,
                    )

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


def search_results(request):
    search_params = request.session.get('search_params', {})
    if not search_params:
        messages.error(request, "Please perform a search first.")
        return redirect('search')

    origin = Airport.objects.get(id=search_params['origin'])
    destination = Airport.objects.get(id=search_params['destination'])
    departure_date = datetime.fromisoformat(search_params['departure_date']).date()
    return_date = datetime.fromisoformat(search_params['return_date']).date() if search_params.get('return_date') else None
    adults = search_params['adults']
    children = search_params['children']
    infants = search_params['infants']
    trip_type = search_params['trip_type']

    total_passengers = adults + children + infants

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

    context = {
        'outbound_flights': outbound_flights,
        'return_flights': return_flights,
        'adults': adults,
        'children': children,
        'infants': infants,
        'trip_type': trip_type
    }
    return render(request, 'flights/search_results.html', context)


def assign_seat(flight, ticket_class):
    class_prefix = 'B' if ticket_class == 'business' else 'E'
    while True:
        row = random.randint(1, 30)
        seat = random.choice('ABCDEF')
        seat_number = f"{class_prefix}{row}{seat}"
        if not Passenger.objects.filter(booking__flight=flight, seat_number=seat_number).exists():
            return seat_number




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
    passengers = booking.passengers.all()
    return render(request, 'flights/booking_confirmation.html', {'booking': booking, 'passengers': passengers})

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

