import secrets
import string
from django.db.models import Sum # type: ignore
from .models import Order
from django.core.validators import validate_email # type: ignore
from django.core.exceptions import ValidationError # type: ignore
import logging
from django.core.mail import send_mail # type: ignore
from django.conf import settings # type: ignore
# Set up logging to capture errors
logger = logging.getLogger(__name__)

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

def send_order_confirmation_email(order_id, customer_email, customer_name, total_price):
    """
    Sends an order confirmation email to the customer.
    """
    subject = f"Order Confirmation - #{order_id}"
    message = (
        f"Hi {customer_name},\n\n"
        f"Thank you for your order! We've received order #{order_id}.\n"
        f"Total Amount: ${total_price}\n\n"
        f"We'll start preparing your food right away!"
    )
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(
            subject,
            message,
            from_email,
            [customer_email],
            fail_silently=False, # Set to False to catch exceptions
        )
        return True, "Email sent successfully."
    
    except Exception as e:
        # This captures connection errors, SMTP issues, etc.
        logger.error(f"Failed to send email for Order {order_id}: {str(e)}")
        return False, f"Could not send email: {str(e)}"         