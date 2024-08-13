# flights/forms.py

from django import forms
from .models import Flight, Airport, Booking
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Flight, Booking, Payment

class SearchForm(forms.Form):
    origin = forms.ModelChoiceField(queryset=Airport.objects.all(), empty_label="Select Origin")
    destination = forms.ModelChoiceField(queryset=Airport.objects.all(), empty_label="Select Destination")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    passengers = forms.IntegerField(min_value=1)

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['passenger_name', 'email', 'age', 'ticket_class', 'food_choice', 'seats']
        widgets = {
            'passenger_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'ticket_class': forms.Select(attrs={'class': 'form-control'}),
            'food_choice': forms.Select(attrs={'class': 'form-control'}),
            'seats': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PaymentForm(forms.ModelForm):
    card_number = forms.CharField(min_length=16, max_length=16, widget=forms.TextInput(attrs={'class': 'form-control'}))
    cvv = forms.CharField(min_length=3, max_length=3, widget=forms.TextInput(attrs={'class': 'form-control'}))
    expiry_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    class Meta:
        model = Payment
        fields = ['card_number', 'cvv', 'expiry_date']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

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