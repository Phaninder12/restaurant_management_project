import secrets
import string
from django.db.models import Sum # type: ignore
from django.core.validators import validate_email # type: ignore
from django.core.exceptions import ValidationError # type: ignore
import logging
from django.core.mail import send_mail # type: ignore
from django.conf import settings # type: ignore
import datetime
# Set up logging to capture errors
logger = logging.getLogger(__name__)


def generate_unique_order_id(length=8):
    """
    Generates a short, unique alphanumeric order identifier.
    The function checks the database for collisions before returning.
    """
    from .models import Order

    characters = string.ascii_uppercase + string.digits

    while True:
        order_id = ''.join(secrets.choice(characters) for _ in range(length))
        if not Order.objects.filter(order_id=order_id).exists():
            return order_id


def generate_coupon_code(length=10):
    """
    Generates a unique, cryptographically secure alphanumeric coupon code.
    """
    from orders.models import Coupon  # Local import prevents circular dependency

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
    # Import locally to avoid circular imports when models import utils
    from .models import Order

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

def send_email(recipient_email, subject, message_body):
    """
    Reusable utility function to send emails.
    
    Args:
        recipient_email (str): The email address of the recipient.
        subject (str): The subject line of the email.
        message_body (str): The body content of the email.
    
    Returns:
        tuple: (success: bool, message: str)
            - success: True if email was sent successfully, False otherwise.
            - message: A descriptive message about the result.
    
    Raises:
        None: All exceptions are caught and returned as part of the tuple.
    """
    # Validate the recipient email
    if not is_valid_email(recipient_email):
        error_msg = f"Invalid recipient email address: {recipient_email}"
        logger.warning(error_msg)
        return False, error_msg
    
    # Get the default from email from settings
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
    
    try:
        # Send the email using Django's send_mail
        send_mail(
            subject=subject,
            message=message_body,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=False,  # Raise exceptions on failure
        )
        success_msg = f"Email sent successfully to {recipient_email}"
        logger.info(success_msg)
        return True, success_msg
    
    except Exception as e:
        # Catch and log any errors (SMTP issues, connection problems, etc.)
        error_msg = f"Failed to send email to {recipient_email}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def format_datetime(dt):
    """
    Formats a datetime object into a user-friendly string.
    
    Args:
        dt (datetime.datetime or None): The datetime object to format.
        
    Returns:
        str: Formatted string like 'January 1, 2023 at 10:30 AM', or empty string if dt is None.
    """
    if dt is None:
        return ""
    
    return f"{dt.strftime('%B')} {dt.day}, {dt.year} at {dt.strftime('%I:%M %p')}"


def calculate_discount(order):
    """
    Calculates the discount amount for an order based on the applied coupon.
    
    Args:
        order: The Order instance.
    
    Returns:
        Decimal: The discount amount.
    """
    from decimal import Decimal
    if order.applied_coupon and order.applied_coupon.is_active:
        discount_percentage = order.applied_coupon.discount_percentage
        discount = (order.total_price * discount_percentage) / Decimal('100')
        return discount
    return Decimal('0.00')         