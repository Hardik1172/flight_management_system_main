from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import  Booking
from .forms import CustomUserCreationForm, SearchForm, BookingForm
from django.shortcuts import render
from .models import Flight, Airport


def index(request):
    domestic_flights = Flight.objects.filter(is_international=False)[:5]
    international_flights = Flight.objects.filter(is_international=True)[:5]
    airports = Airport.objects.all()[:5]
    return render(request, 'flights/index.html', {
        'domestic_flights': domestic_flights,
        'international_flights': international_flights,
        'airports': airports
    })



@require_http_methods(["GET", "POST"])
def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            date = form.cleaned_data['date']
            flights = Flight.objects.filter(
                origin__city__icontains=origin,
                destination__city__icontains=destination,
                departure_time__date=date
            )
            return JsonResponse({'flights': list(flights.values())})
    else:
        form = SearchForm()
    return render(request, 'flights/search.html', {'form': form})

@login_required
@require_http_methods(["GET", "POST"])
def book(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            if flight.available_seats > 0:
                booking = Booking.objects.create(
                    user=request.user,
                    flight=flight,
                    seat_number=form.cleaned_data['seat_number']
                )
                flight.available_seats -= 1
                flight.save()
                return JsonResponse({'success': True, 'booking_id': booking.id})
            else:
                return JsonResponse({'success': False, 'error': 'No available seats'})
    else:
        form = BookingForm()
    return render(request, 'flights/book.html', {'form': form, 'flight': flight})

@login_required
def bookings(request):
    user_bookings = Booking.objects.filter(user=request.user)
    return render(request, 'flights/bookings.html', {'bookings': user_bookings})

def contact(request):
    return render(request, 'flights/contact.html')

@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'flights/register.html', {'form': form})



@login_required()
def payment(request):
    return render(request, 'flights/payment.html')

@login_required
def payment_process(request):
    # Implement actual payment processing here
    return JsonResponse({'success': True})

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