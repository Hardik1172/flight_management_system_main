from django import forms
from .models import Flight, Airport, Booking, Payment, Stopover
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from decimal import Decimal
from django import forms
from .models import Passenger
from django.forms import modelformset_factory


class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'passenger_type', 'meal_choice', 'seat_class']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'passenger_type': forms.HiddenInput(),
            'meal_choice': forms.Select(attrs={'class': 'form-control'}),
            'seat_class': forms.Select(attrs={'class': 'form-control'}),
        }

PassengerFormSet = modelformset_factory(Passenger, form=PassengerForm, extra=0)



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
    adults = forms.IntegerField(min_value=1, initial=1)
    children = forms.IntegerField(min_value=0, initial=0)
    infants = forms.IntegerField(min_value=0, initial=0)


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
