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
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Flight, Booking, Passenger, Stopover
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Flight, Airport, Booking, Payment, Stopover, Passenger

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, required=True, label='Register as')

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'user_type')

class CustomAuthenticationForm(forms.Form):
    username = forms.CharField(max_length=254)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, required=True, label='Login as')



class DateInput(forms.DateInput):
    input_type = 'date'

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'passenger_type', 'ticket_class', 'meal_choice']
        widgets = {
            'passenger_type': forms.HiddenInput(),
            'ticket_class': forms.Select(attrs={'class': 'form-control'}),
            'meal_choice': forms.Select(attrs={'class': 'form-control'}),
        }
class SearchForm(forms.Form):
    TRIP_CHOICES = (
        ('one_way', 'One Way'),
        ('round_trip', 'Round Trip'),
    )
    trip_type = forms.ChoiceField(choices=TRIP_CHOICES, widget=forms.RadioSelect)
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
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'min': timezone.now().date().isoformat()})
    )
    return_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'min': timezone.now().date().isoformat()}),
        required=False
    )
    adults = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    children = forms.IntegerField(min_value=0, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    infants = forms.IntegerField(min_value=0, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        origin = cleaned_data.get('origin')
        destination = cleaned_data.get('destination')
        departure_date = cleaned_data.get('departure_date')
        return_date = cleaned_data.get('return_date')

        if origin and destination and origin == destination:
            raise forms.ValidationError("From & To airports cannot be the same.")

        if departure_date and departure_date < timezone.now().date():
            raise forms.ValidationError("Departure date cannot be in the past.")

        if return_date and return_date < departure_date:
            raise forms.ValidationError("Return date must be after departure date.")

        return cleaned_data

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['card_number', 'cvv', 'expiry_date']
        widgets = {
            'card_number': forms.TextInput(attrs={'class': 'form-control'}),
            'cvv': forms.TextInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        if expiry_date < timezone.now().date():
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
                  'economy_price', 'business_price', 'economy_seats', 'business_seats',
                  'available_economy_seats', 'available_business_seats', 'is_international', 'day_of_week']
        widgets = {
            'flight_number': forms.TextInput(attrs={'class': 'form-control'}),
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'economy_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'business_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'economy_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'business_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_economy_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_business_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_international': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        origin = cleaned_data.get('origin')
        destination = cleaned_data.get('destination')
        departure_time = cleaned_data.get('departure_time')
        arrival_time = cleaned_data.get('arrival_time')
        economy_seats = cleaned_data.get('economy_seats')
        business_seats = cleaned_data.get('business_seats')
        available_economy_seats = cleaned_data.get('available_economy_seats')
        available_business_seats = cleaned_data.get('available_business_seats')

        if origin and destination and origin == destination:
            raise forms.ValidationError("Origin and destination cannot be the same.")

        if departure_time and arrival_time and departure_time >= arrival_time:
            raise forms.ValidationError("Departure time must be before arrival time.")

        if economy_seats is not None and available_economy_seats is not None:
            if available_economy_seats > economy_seats:
                raise forms.ValidationError("Available economy seats cannot exceed total economy seats.")

        if business_seats is not None and available_business_seats is not None:
            if available_business_seats > business_seats:
                raise forms.ValidationError("Available business seats cannot exceed total business seats.")

        return cleaned_data

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
        fields = ['ticket_class']
        widgets = {
            'ticket_class': forms.Select(attrs={'class': 'form-control'}),
        }







