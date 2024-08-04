from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Flight, Booking
from .forms import FlightSearchForm, BookingForm
import random


def home(request):
    return render(request, 'flights/home.html')


def search_flights(request):
    if request.method == 'POST':
        form = FlightSearchForm(request.POST)
        if form.is_valid():
            flights = Flight.objects.filter(
                source=form.cleaned_data['source'],
                destination=form.cleaned_data['destination'],
                date=form.cleaned_data['date']
            )
            return render(request, 'flights/flight_list.html', {'flights': flights})
    else:
        form = FlightSearchForm()
    return render(request, 'flights/search_flights.html', {'form': form})


@login_required
def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.flight = flight
            booking.seat_number = f"{random.choice('ABCDEF')}{random.randint(1, 30)}"
            booking.save()
            flight.available_seats -= 1
            flight.save()
            return redirect('payment', booking_ids=booking.id)
    else:
        form = BookingForm()
    return render(request, 'flights/book_flight.html', {'flight': flight, 'form': form})


@login_required
def dashboard(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'flights/dashboard.html', {'bookings': bookings})


@login_required
def payment(request, booking_ids):
    booking_id_list = booking_ids.split(',')
    bookings = Booking.objects.filter(id__in=booking_id_list, user=request.user)

    if not bookings.exists():
        messages.error(request, "No valid bookings found.")
        return redirect('dashboard')

    total_price = sum(booking.flight.price for booking in bookings)

    if request.method == 'POST':
        # Process the payment here
        # This is where you'd integrate with a payment gateway
        # For now, we'll just mark the booking as paid
        for booking in bookings:
            booking.paid = True
            booking.save()
        messages.success(request, "Payment successful!")
        return redirect('booking_confirmation', booking_ids=booking_ids)

    return render(request, 'flights/payment.html', {
        'bookings': bookings,
        'total_price': total_price
    })

@login_required
def view_bookings(request):
    return dashboard(request)
@login_required
def booking_confirmation(request, booking_ids):
    booking_id_list = booking_ids.split(',')
    bookings = Booking.objects.filter(id__in=booking_id_list, user=request.user, paid=True)

    if not bookings.exists():
        messages.error(request, "No confirmed bookings found.")
        return redirect('dashboard')

    return render(request, 'flights/booking_confirmation.html', {'bookings': bookings})


def about(request):
    return render(request, 'flights/about.html')


def contact(request):
    if request.method == 'POST':
        # Process contact form
        messages.success(request, "Your message has been sent. We'll get back to you soon!")
        return redirect('contact')
    return render(request, 'flights/contact.html')