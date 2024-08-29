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
from  django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking, Passenger
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Booking, Passenger
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm
from django.contrib.auth import login, authenticate, logout, get_user_model
from .forms import CustomUserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser
from django.contrib.auth.views import LoginView

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
        passenger_forms = [PassengerForm(request.POST, prefix=f'passenger-{i}') for i in range(total_passengers)]

        if booking_form.is_valid() and all(form.is_valid() for form in passenger_forms):
            ticket_class = booking_form.cleaned_data['ticket_class']

            # Check seat availability
            if ticket_class == 'economy' and flight.available_economy_seats < total_passengers:
                messages.error(request, "Not enough economy seats available for this flight.")
                return render(request, 'flights/book.html',
                              {'booking_form': booking_form, 'passenger_forms': passenger_forms, 'flight': flight,
                               'return_flight': return_flight})
            elif ticket_class == 'business' and flight.available_business_seats < total_passengers:
                messages.error(request, "Not enough business seats available for this flight.")
                return render(request, 'flights/book.html',
                              {'booking_form': booking_form, 'passenger_forms': passenger_forms, 'flight': flight,
                               'return_flight': return_flight})

            # If seats are available, proceed with booking
            booking = booking_form.save(commit=False)
            booking.user = request.user
            booking.flight = flight
            booking.return_flight = return_flight
            booking.status = 'Pending'  # Change status to 'Pending' until payment is confirmed
            booking.adults = adults
            booking.children = children
            booking.infants = infants
            booking.save()

            # Save passengers
            for form in passenger_forms:
                passenger = form.save(commit=False)
                passenger.booking = booking
                passenger.save()

            # Update available seats
            if ticket_class == 'economy':
                flight.available_economy_seats -= total_passengers
            else:
                flight.available_business_seats -= total_passengers
            flight.save()

            if return_flight:
                if ticket_class == 'economy':
                    return_flight.available_economy_seats -= total_passengers
                else:
                    return_flight.available_business_seats -= total_passengers
                return_flight.save()

            return redirect('payment', booking_id=booking.id)
    else:
        booking_form = BookingForm()
        passenger_forms = [PassengerForm(prefix=f'passenger-{i}') for i in range(total_passengers)]

    context = {
        'booking_form': booking_form,
        'passenger_forms': passenger_forms,
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
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'flights/bookings.html', {'bookings': bookings})


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'flights/booking_detail.html', {'booking': booking})


def get_destinations(request, origin_id):
    destinations = Airport.objects.exclude(id=origin_id).values('id', 'name', 'code')
    return JsonResponse(list(destinations), safe=False)

@login_required
def cancel_booking(request):
    if request.method == 'POST':
        passenger_id = request.POST.get('passenger_id')
        try:
            passenger = Passenger.objects.get(passenger_id=passenger_id)
            if passenger.booking.user != request.user:
                messages.error(request, "You don't have permission to cancel this booking.")
                return redirect('cancel_booking')
            return render(request, 'flights/cancel_booking.html', {'passenger': passenger})
        except Passenger.DoesNotExist:
            messages.error(request, "No passenger found with this ID.")
    return render(request, 'flights/cancel_booking.html')



@login_required
def confirm_cancel_booking(request, passenger_id):
    passenger = get_object_or_404(Passenger, passenger_id=passenger_id)
    if passenger.booking.user != request.user:
        messages.error(request, "You don't have permission to cancel this booking.")
        return redirect('cancel_booking')

    if request.method == 'POST':
        if not passenger.is_cancelled:
            passenger.cancel()
            messages.success(request, f"Booking for passenger {passenger.first_name} {passenger.last_name} has been cancelled.")
        else:
            messages.error(request, "This booking is already cancelled.")
        return redirect('bookings')

    context = {
        'passenger': passenger,
        'booking': passenger.booking
    }
    return render(request, 'flights/confirm_cancel_booking.html', context)



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

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('index')
        else:
            messages.error(request, 'Registration failed. Please correct the errors.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'flights/register.html', {'form': form})

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user_type = form.cleaned_data.get('user_type')
        user = authenticate(self.request, username=username, password=password)
        if user is not None and user.user_type == user_type:
            login(self.request, user)
            messages.success(self.request, f'Welcome, {username}!')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Invalid username, password, or user type.')
            return self.form_invalid(form)

def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'


@require_http_methods(["GET", "POST"])
def user_logout(request):
    logout(request)
    return redirect('index')



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












