from django import template

register = template.Library()

@register.filter
def bookings_for_date(bookings, date):
    """Фильтрует записи по указанной дате"""
    return [b for b in bookings if b.date_of_lesson == date]