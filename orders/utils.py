import secrets
import string
from django.db.models import Sum # type: ignore
from .models import Order
from django.core.validators import validate_email # type: ignore
from django.core.exceptions import ValidationError # type: ignore
import logging


def generate_coupon_code(length=10):
    """
    Generates a unique, cryptographically secure alphanumeric coupon code.
    """
    from orders.models import Coupon # Local import prevents circular dependency
    
    characters = string.ascii_uppercase + string.digits
    
    while True:
        code = ''.join(secrets.choice(characters) for _ in range(length))
        
        # Check if the code already exists in the database
        if not Coupon.objects.filter(code=code).exists():
            return code

def get_daily_sales_total(date):
    """
    Calculates the total revenue for a specific date.
    
    Args:
        date (datetime.date): The date to calculate sales for.
        
    Returns:
        Decimal: The total sum of all orders on that day, or 0 if no orders exist.
    """
    # 1. Filter orders by the specific date
    # 2. Aggregate the 'total_price' field using Sum
    daily_orders = Order.objects.filter(created_at__date=date)
    
    aggregation = daily_orders.aggregate(total_sum=Sum('total_price'))
    
    # Extract the sum from the dictionary; return 0 if the result is None
    total = aggregation['total_sum']
    
    return total if total is not None else 0

# Set up logging to track validation issues if needed
logger = logging.getLogger(__name__)

def is_valid_email(email_address):
    """
    Validates an email address using Django's built-in validator.
    Returns True if valid, False otherwise.
    """
    if not email_address:
        return False

    try:
        # Django's validate_email will raise a ValidationError if the email is invalid
        validate_email(email_address)
        return True
    except ValidationError:
        # Log the attempt if you want to track suspicious input
        logger.warning(f"Invalid email attempt: {email_address}")
        return False
    except Exception as e:
        # Catch unexpected errors to prevent application crashes
        logger.error(f"Unexpected error during email validation: {e}")
        return False        