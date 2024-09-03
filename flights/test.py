from kafka import KafkaProducer, KafkaConsumer
from django.conf import settings
import json

def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def get_kafka_consumer(topic):
    return KafkaConsumer(
        topic,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

def produce_message(topic, message):
    producer = get_kafka_producer()
    producer.send(topic, message)
    producer.flush()

def consume_messages(topic, callback):
    consumer = get_kafka_consumer(topic)
    for message in consumer:
        callback(message.value)

views.py

from .kafka_utils import produce_message
from django.conf import settings


@login_required
def book(request, flight_id, return_flight_id=None):
    # ... (existing code) ...

    if form.is_valid():
        booking = form.save()

        # Produce a Kafka message for the new booking
        produce_message(settings.KAFKA_BOOKING_NOTIFICATIONS_TOPIC, {
            'booking_id': booking.id,
            'user_id': request.user.id,
            'flight_id': flight_id,
            'return_flight_id': return_flight_id
        })

        return redirect('payment', booking_id=booking.id)

    # ... (rest of the function)


@login_required
def payment(request, booking_id):
    # ... (existing code) ...

    if payment_form.is_valid():
        # Process payment here
        booking.status = 'Confirmed'
        booking.save()

        # Produce a Kafka message for the payment event
        produce_message(settings.KAFKA_PAYMENT_EVENTS_TOPIC, {
            'booking_id': booking_id,
            'user_id': request.user.id,
            'amount': str(total_price)
        })

        messages.success(request, "Payment successful. Your booking is confirmed.")
        return redirect('booking_confirmation', booking_id=booking.id)

    # ... (rest of the function)


def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            # ... (existing code) ...

            # Produce a Kafka message for search analytics
            produce_message(settings.KAFKA_SEARCH_ANALYTICS_TOPIC, {
                'user_id': request.user.id if request.user.is_authenticated else None,
                'origin': form.cleaned_data['origin'].id,
                'destination': form.cleaned_data['destination'].id,
                'departure_date': form.cleaned_data['departure_date'].isoformat(),
                'return_date': form.cleaned_data['return_date'].isoformat() if form.cleaned_data[
                    'return_date'] else None,
            })

            return redirect('search_results')

    # ... (rest of the function)


# kafka consumers management command

from django.core.management.base import BaseCommand
from django.conf import settings
from flights.kafka_utils import consume_messages
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs Kafka consumers for various topics'

    def handle(self, *args, **options):
        def process_flight_updates(message):
            logger.info(f"Received flight update: {message}")
            # Process flight update logic here

        def process_booking_notifications(message):
            logger.info(f"Received booking notification: {message}")
            # Process booking notification logic here

        def process_payment_events(message):
            logger.info(f"Received payment event: {message}")
            # Process payment event logic here

        def process_search_analytics(message):
            logger.info(f"Received search analytics: {message}")
            # Process search analytics logic here

        consume_messages(settings.KAFKA_FLIGHT_UPDATES_TOPIC, process_flight_updates)
        consume_messages(settings.KAFKA_BOOKING_NOTIFICATIONS_TOPIC, process_booking_notifications)
        consume_messages(settings.KAFKA_PAYMENT_EVENTS_TOPIC, process_payment_events)
        consume_messages(settings.KAFKA_SEARCH_ANALYTICS_TOPIC, process_search_analytics)

# kafka configuration in settings.py

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']  # Replace with your Kafka broker address
KAFKA_FLIGHT_UPDATES_TOPIC = 'flight_updates'
KAFKA_BOOKING_NOTIFICATIONS_TOPIC = 'booking_notifications'
KAFKA_PAYMENT_EVENTS_TOPIC = 'payment_events'
KAFKA_SEARCH_ANALYTICS_TOPIC = 'search_analytics'
KAFKA_USER_ACTIVITY_TOPIC = 'user_activity'






