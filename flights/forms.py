from django import forms
from .models import Flight, Booking

class FlightSearchForm(forms.Form):
    source = forms.CharField(max_length=100)
    destination = forms.CharField(max_length=100)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = []  # We'll set the user and flight in the view