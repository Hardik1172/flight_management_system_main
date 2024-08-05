from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class SearchForm(forms.Form):
    origin = forms.CharField(max_length=100)
    destination = forms.CharField(max_length=100)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    passengers = forms.IntegerField(min_value=1, max_value=10)

class BookingForm(forms.Form):
    seat_number = forms.CharField(max_length=5)