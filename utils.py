import re
from decimal import Decimal
from datetime import datetime, time
from orders.models import Order
from restaurant_management.utils import format_phone_number

def format_phone_number(phone_str):
    """
    Formats a string into a standard phone format: (XXX) XXX-XXXX
    """
    try:
        cleaned = re.sub(r'\D', '', str(phone_str))

        if len(cleaned) == 10:
            return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
        elif len(cleaned) == 11 and cleaned.startswith('1'):
            return f"+1 ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:]}"
        else:
            return phone_str
    except Exception as e:
        print(f"Error formatting phone number: {e}")
        return phone_str

def calculate_discount(order):
    """
    Calculates discount based on applied coupon percentage.
    """
    if order.applied_coupon:
        percentage = order.applied_coupon.discount_percentage
        discount = (order.total_price * percentage) / Decimal('100')
        return discount
    return Decimal('0.00')

def is_reservation_time_valid(proposed_datetime, operating_hours_model):
    """
    Checks if a proposed reservation fits within the restaurant's operating hours.
    """
    day_name = proposed_datetime.strftime('%A') 
    
    try:
        hours = operating_hours_model.objects.get(day=day_name)
    except operating_hours_model.DoesNotExist:
        return False

    reservation_time = proposed_datetime.time()
    
    # Check if time is within open hours
    if hours.opening_time <= reservation_time <= hours.closing_time:
        return True
    
    return False

def staff_dashboard(request):
    orders = Order.objects.all()
    for order in orders:
        # Dynamically format the phone number for display
        order.formatted_phone = format_phone_number(order.customer_phone)
    
    return render(request, 'dashboard.html', {'orders': orders}) # type: ignore