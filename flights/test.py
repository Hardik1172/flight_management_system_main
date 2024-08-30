from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking, Passenger
from django.db.models import Prefetch, Exists, OuterRef
import logging

logger = logging.getLogger(__name__)

@login_required
def bookings(request):
    bookings = Booking.objects.filter(user=request.user).prefetch_related(
        Prefetch('passengers', queryset=Passenger.objects.order_by('id'))
    ).order_by('-booking_date')

    return render(request, 'flights/bookings.html', {'bookings': bookings})

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