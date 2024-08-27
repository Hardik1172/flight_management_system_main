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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking, Payment, Passenger
from .forms import PaymentForm
from django.utils import timezone
from django.urls import reverse
from django.db.utils import IntegrityError
from django.core.serializers import serialize
from django.http import JsonResponse
from .models import Airport


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
            request.session['search_params'] = {
                'origin': form.cleaned_data['origin'].id,
                'destination': form.cleaned_data['destination'].id,
                'departure_date': form.cleaned_data['departure_date'].isoformat(),
                'return_date': form.cleaned_data['return_date'].isoformat() if form.cleaned_data[
                    'return_date'] else None,
                'adults': form.cleaned_data['adults'],
                'children': form.cleaned_data['children'],
                'infants': form.cleaned_data['infants'],
                'trip_type': form.cleaned_data['trip_type']
            }

            return redirect('search_results')
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = SearchForm()

    search_history = SearchHistory.objects.filter(user=request.user).order_by('-search_date')[
                     :5] if request.user.is_authenticated else []

    context = {
        'form': form,
        'search_history': search_history
    }
    return render(request, 'flights/search.html', context)


# flights/views.py

@login_required
def book(request, flight_id, return_flight_id=None):
    flight = get_object_or_404(Flight, pk=flight_id)
    return_flight = None
    if return_flight_id:
        return_flight = get_object_or_404(Flight, pk=return_flight_id)

    search_params = request.session.get('search_params', {})
    adults = int(search_params.get('adults', 0))
    children = int(search_params.get('children', 0))
    infants = int(search_params.get('infants', 0))
    total_passengers = adults + children + infants

    if request.method == 'POST':
        booking_form = BookingForm(request.POST)
        if booking_form.is_valid():
            ticket_class = booking_form.cleaned_data['ticket_class']

            if flight.available_economy_seats & flight.available_business_seats< total_passengers:
                messages.error(request, "Not enough seats available for this flight.")
                return render(request, 'flights/book.html',
                              {'booking_form': booking_form, 'flight': flight, 'return_flight': return_flight})

            booking = booking_form.save(commit=False)
            booking.user = request.user
            booking.flight = flight
            booking.return_flight = return_flight
            booking.status = 'Confirmed'
            booking.adults = adults
            booking.children = children
            booking.infants = infants
            booking.save()

            flight.update_available_seats()
            if return_flight:
                return_flight.update_available_seats()

            # Process passenger forms
            for i in range(total_passengers):
                passenger_form = PassengerForm(request.POST, prefix=f'passenger-{i}')
                if passenger_form.is_valid():
                    passenger = passenger_form.save(commit=False)
                    passenger.booking = booking
                    passenger.save()

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
def bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('flight').prefetch_related('passengers').order_by('-booking_date')
    return render(request, 'flights/bookings.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking.objects.prefetch_related('passengers'), id=booking_id, user=request.user)
    return render(request, 'flights/booking_detail.html', {'booking': booking})


def get_destinations(request, origin_id):
    destinations = Airport.objects.exclude(id=origin_id).values('id', 'name', 'code')
    return JsonResponse(list(destinations), safe=False)

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == 'Confirmed':
        booking.cancel()
        messages.success(request, "Your booking has been successfully cancelled.")
    else:
        messages.error(request, "This booking cannot be cancelled.")
    return redirect('booking_detail.html', booking_id=booking.id)

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
        available_economy_seats__gte=total_passengers,
        available_business_seats__gte=total_passengers
    ).prefetch_related('stopovers')

    return_flights = None
    if trip_type == 'round_trip' and return_date:
        return_flights = Flight.objects.filter(
            origin=destination,
            destination=origin,
            departure_time__date=return_date,
            available_economy_seats__gte=total_passengers,
            available_business_seats__gte=total_passengers
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
def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    total_price = booking.total_price()

    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            # Process payment here (you would typically integrate with a payment gateway)
            booking.status = 'Confirmed'
            booking.save()
            messages.success(request, "Payment successful. Your booking is confirmed.")
            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        payment_form = PaymentForm()

    context = {
        'booking': booking,
        'payment_form': payment_form,
        'total_price': total_price,
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
            try:
                user = form.save()
                login(request, user)
                messages.success(request, "Registration successful.")
                return redirect("index")
            except IntegrityError:
                messages.error(request, "A user with that username already exists. Please choose a different username.")
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
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












