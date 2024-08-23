

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.urls import reverse
from .models import Flight, Booking, Passenger
from .forms import BookingForm, PassengerForm, PaymentForm
from django.utils import timezone


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

    PassengerFormSet = formset_factory(PassengerForm, extra=total_passengers)

    if request.method == 'POST':
        booking_form = BookingForm(request.POST)
        passenger_formset = PassengerFormSet(request.POST, prefix='passenger')

        if booking_form.is_valid() and passenger_formset.is_valid():
            booking = Booking.objects.create(
                user=request.user,
                flight=flight,
                return_flight=return_flight,
                status='Pending',
                adults=adults,
                children=children,
                infants=infants
            )

            passenger_types = ['adult'] * adults + ['child'] * children + ['infant'] * infants
            for form, p_type in zip(passenger_formset, passenger_types):
                passenger = form.save(commit=False)
                passenger.booking = booking
                passenger.passenger_type = p_type
                passenger.save()

            return redirect(reverse('payment', kwargs={'booking_id': booking.id}))
    else:
        initial_data = {
            'departure_date': max(flight.departure_time.date(), timezone.now().date()),
            'return_date': return_flight.departure_time.date() if return_flight else None
        }
        booking_form = BookingForm(initial=initial_data)
        passenger_formset = PassengerFormSet(prefix='passenger')

    context = {
        'booking_form': booking_form,
        'passenger_formset': passenger_formset,
        'flight': flight,
        'return_flight': return_flight,
        'adults': adults,
        'children': children,
        'infants': infants,
        'total_passengers': total_passengers,
    }
    return render(request, 'flights/book.html', context)


@login_required
def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            # Process payment here
            booking.status = 'Confirmed'
            booking.save()
            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        payment_form = PaymentForm()

    return render(request, 'flights/payment.html', {'booking': booking, 'payment_form': payment_form})


# Add this new view
@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'flights/booking_confirmation.html', {'booking': booking})



from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_results, name='search_results'),
    path('book/<int:flight_id>/', views.book, name='book'),
    path('book/<int:flight_id>/<int:return_flight_id>/', views.book, name='book_round_trip'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('booking_confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
]



from django import forms
from .models import Booking, Passenger
from django.utils import timezone


class DateInput(forms.DateInput):
    input_type = 'date'


class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'ticket_class', 'meal_choice']


class BookingForm(forms.ModelForm):
    departure_date = forms.DateField(widget=DateInput(), required=False)
    return_date = forms.DateField(widget=DateInput(), required=False)

    class Meta:
        model = Booking
        fields = ['departure_date', 'return_date']

    def clean(self):
        cleaned_data = super().clean()
        departure_date = cleaned_data.get('departure_date')
        return_date = cleaned_data.get('return_date')
        today = timezone.now().date()

        if departure_date and departure_date < today:
            raise forms.ValidationError("Departure date cannot be in the past.")

        if return_date and return_date < today:
            raise forms.ValidationError("Return date cannot be in the past.")

        if departure_date and return_date and return_date < departure_date:
            raise forms.ValidationError("Return date must be after departure date.")

        return cleaned_data


class PaymentForm(forms.Form):
    card_number = forms.CharField(max_length=16, min_length=16)
    expiry_date = forms.DateField(widget=DateInput())
    cvv = forms.CharField(max_length=3, min_length=3)

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        if expiry_date < timezone.now().date():
            raise forms.ValidationError("Expiry date cannot be in the past.")
        return expiry_date



from django.shortcuts import render, redirect
from .forms import FlightSearchForm
from .models import Flight
from django.utils import timezone

def search_flights(request):
    if request.method == 'POST':
        form = FlightSearchForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            departure_date = form.cleaned_data['departure_date']
            return_date = form.cleaned_data['return_date']
            adults = form.cleaned_data['adults']
            children = form.cleaned_data['children']
            infants = form.cleaned_data['infants']

            # Store search parameters in session
            request.session['search_params'] = {
                'origin': origin.id,
                'destination': destination.id,
                'departure_date': departure_date.isoformat(),
                'return_date': return_date.isoformat() if return_date else None,
                'adults': adults,
                'children': children,
                'infants': infants,
            }

            # Perform the search
            outbound_flights = Flight.objects.filter(
                origin=origin,
                destination=destination,
                departure_time__date=departure_date
            )

            return_flights = None
            if return_date:
                return_flights = Flight.objects.filter(
                    origin=destination,
                    destination=origin,
                    departure_time__date=return_date
                )

            return render(request, 'flights/search_results.html', {
                'outbound_flights': outbound_flights,
                'return_flights': return_flights,
            })
    else:
        form = FlightSearchForm(initial={'departure_date': timezone.now().date()})

    return render(request, 'flights/search.html', {'form': form})