from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={'class': css_class})

@register.filter
def active_passenger_count(booking):
    return booking.passengers.filter(is_cancelled=False).count()