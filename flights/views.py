# flights/views.py

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render

import logging
import random
from datetime import datetime
from .forms import BookingWithPassengersForm
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .forms import FlightForm, StopoverInlineFormSet
from .forms import PaymentForm
from .forms import SearchForm
from .models import Airport
from .models import Booking, Passenger
from .models import Flight
from .models import SearchHistory

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
            # Only save search history for authenticated users
            if request.user.is_authenticated:
                SearchHistory.objects.create(
                    user=request.user,
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
                'return_date': form.cleaned_data['return_date'].isoformat() if form.cleaned_data['return_date'] else None,
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

    search_history = SearchHistory.objects.filter(user=request.user).order_by('-search_date')[:5] if request.user.is_authenticated else []

    context = {
        'form': form,
        'search_history': search_history
    }
    return render(request, 'flights/search.html', context)







# views.py



@login_required
def book(request, flight_id, return_flight_id=None):
    if request.user.user_type != 'passenger':
        messages.error(request, " Booking is only available for passenger user ")
        return redirect('index')

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
        form = BookingWithPassengersForm(request.POST, extra=total_passengers)
        if form.is_valid():
            booking = Booking(
                user=request.user,
                flight=flight,
                return_flight=return_flight,
                status='Confirmed',
                adults=adults,
                children=children,
                infants=infants
            )
            booking.save()


            for passenger_form in form.passenger_forms:
                passenger = passenger_form.save(commit=False)
                passenger.booking = booking
                passenger.save()

            # Update available seats
            flight.available_economy_seats -= total_passengers
            flight.available_business_seats -= total_passengers
            flight.save()

            if return_flight:
                return_flight.available_economy_seats -= total_passengers
                return_flight.available_business_seats -= total_passengers
                return_flight.save()

            return redirect('payment', booking_id=booking.id)
    else:
        form = BookingWithPassengersForm(extra=total_passengers)

    context = {
        'form': form,
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
    bookings = Booking.objects.filter(user=request.user).prefetch_related(
        Prefetch('passengers', queryset=Passenger.objects.order_by('id'))
    ).order_by('-booking_date')

    for booking in bookings:
        booking.has_active = booking.has_active_passengers()

    return render(request, 'flights/bookings.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    passengers = booking.passengers.all().order_by('id')
    logger.debug(f"Booking detail for booking {booking_id}")
    logger.debug(f"Number of passengers: {passengers.count()}")
    for passenger in passengers:
        logger.debug(f"Passenger: {passenger.id}, {passenger.first_name} {passenger.last_name}")
    return render(request, 'flights/booking_detail.html', {'booking': booking, 'passengers': passengers})


def get_destinations(request, origin_id):
    destinations = Airport.objects.exclude(id=origin_id).values('id', 'name', 'code')
    return JsonResponse(list(destinations), safe=False)


@login_required
def cancel_booking(request):
    if request.method == 'POST':
        passenger_id = request.POST.get('passenger_id')
        try:
            passenger = Passenger.objects.select_related('booking__flight').get(passenger_id=passenger_id)
            if passenger.booking.user != request.user:
                messages.error(request, "You don't have permission to cancel this booking.")
                return redirect('cancel_booking')

            context = {
                'passenger': passenger,
                'booking': passenger.booking,
            }
            return render(request, 'flights/confirm_cancel_booking.html', context)
        except Passenger.DoesNotExist:
            messages.error(request, "No passenger found with this ID.")
    return render(request, 'flights/cancel_booking.html')

@login_required
def confirm_cancel_booking(request, passenger_id):
    try:
        passenger = Passenger.objects.select_related('booking__flight').get(passenger_id=passenger_id)
        if passenger.booking.user != request.user:
            messages.error(request, "You don't have permission to cancel this booking.")
            return redirect('cancel_booking')

        if request.method == 'POST':
            if not passenger.is_cancelled:
                passenger.is_cancelled = True
                passenger.save()

                # Update available seats
                flight = passenger.booking.flight
                if passenger.ticket_class == 'economy':
                    flight.available_economy_seats = min(flight.economy_seats, flight.available_economy_seats + 1)
                else:
                    flight.available_business_seats = min(flight.business_seats, flight.available_business_seats + 1)
                flight.save()

                messages.success(request, f"Booking for passenger {passenger.first_name} {passenger.last_name} has been cancelled.")
            else:
                messages.error(request, "This booking is already cancelled.")
            return redirect('bookings')

        context = {
            'passenger': passenger,
            'booking': passenger.booking
        }
        return render(request, 'flights/confirm_cancel_booking.html', context)
    except Passenger.DoesNotExist:
        messages.error(request, "No passenger found with this ID.")
        return redirect('cancel_booking')




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
        'trip_type': trip_type,
        'is_admin': request.user.is_authenticated and request.user.user_type == 'admin'
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

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! You've successfully registered as a {user.get_user_type_display()}.")
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'flights/register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user_type = form.cleaned_data.get('user_type')
            user = authenticate(username=username, password=password)
            if user is not None and user.user_type == user_type:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('index')
            else:
                messages.error(request, "Invalid username, password, or user type.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You've been successfully logged out.")
    return redirect('index')

def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin' and user.user_type != 'passenger'


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'flights/admin_dashboard.html')


@login_required
@user_passes_test(is_admin)
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












