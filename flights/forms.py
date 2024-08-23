from django import forms
from .models import Flight, Airport, Booking, Payment, Stopover
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from decimal import Decimal
from django import forms
from .models import Passenger
from django.forms import modelformset_factory
from django.utils import timezone
import datetime
from django.core.validators import MinValueValidator
from django.db import models


class DateInput(forms.DateInput):
    input_type = 'date'
class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'passenger_type', 'ticket_class', 'meal_choice']
        widgets = {
            'passenger_type': forms.HiddenInput(),
        }

class SearchForm(forms.Form):
    TRIP_CHOICES = (
        ('one_way', 'One Way'),
        ('round_trip', 'Round Trip'),
    )
    trip_type = forms.ChoiceField(choices=TRIP_CHOICES, widget=forms.RadioSelect)
    origin = forms.ModelChoiceField(queryset=Airport.objects.all(), empty_label="Select Origin")
    destination = forms.ModelChoiceField(queryset=Airport.objects.all(), empty_label="Select Destination")
    departure_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    return_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    adults = forms.IntegerField(min_value=0, initial=0)
    children = forms.IntegerField(min_value=0, initial=0)
    infants = forms.IntegerField(min_value=0, initial=0)

    class Meta:
        model = Booking
        fields = ['departure_date', 'return_date']






class PaymentForm(forms.Form):
    card_number = forms.CharField(max_length=16, min_length=16)
    expiry_date = forms.DateField(widget=DateInput())
    cvv = forms.CharField(max_length=3, min_length=3)


    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        if expiry_date < timezone.now().date() :
             raise forms.ValidationError("Expiry date cannot be in the past.")
        return expiry_date


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)


    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class FlightForm(forms.ModelForm):
    origin = forms.ModelChoiceField(
        queryset=Airport.objects.all(),
        empty_label="Select Origin",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    destination = forms.ModelChoiceField(
        queryset=Airport.objects.all(),
        empty_label="Select Destination",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Flight
        fields = ['flight_number', 'origin', 'destination', 'departure_time', 'arrival_time',
                  'economy_price', 'business_price', 'available_seats', 'is_international', 'day_of_week']
        widgets = {
            'flight_number': forms.TextInput(attrs={'class': 'form-control'}),
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'economy_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'business_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_international': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
        }

class StopoverFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data['arrival_time'] >= form.cleaned_data['departure_time']:
                    raise forms.ValidationError("Stopover arrival time must be before departure time.")

StopoverInlineFormSet = forms.inlineformset_factory(
    Flight, Stopover, formset=StopoverFormSet,
    fields=('airport', 'arrival_time', 'departure_time'),
    extra=1,
    widgets={
        'airport': forms.Select(attrs={'class': 'form-control'}),
        'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
    }
)

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = []
    def clean(self):

        cleaned_data = super().clean()
        departure_date = cleaned_data.get('departure_date')
        return_date = cleaned_data.get('return_date')
        today = timezone.now().date()
        expiry_date = cleaned_data.get('expiry_date')
        destination_airport = Airport.objects.all().except("Airport used in origin")
        origin_airport = Airport.objects.all().except("Airports used in destination")


        if departure_date and departure_date < today:
            return forms.ValidationError("Departure Date not valid")

        if return_date and return_date < today:
            return forms.ValidationError("Return Date cannot  be passed")

        if departure_date and return_date < departure_date :
            return forms.ValidationError("Return Date cannot be smaller than departure_date")

        if expiry_date and expiry_date < today :
            return forms.ValidationError("Expiry date cannot be passed")

        if destination_airport == origin_airport :
            return forms.ValidationError("destination and orign airport cannot be same . plz select differnt airport from one of them ")

        return cleaned_data

def get_total_passengers(self):
    return self.adults + self.child + self.infant






