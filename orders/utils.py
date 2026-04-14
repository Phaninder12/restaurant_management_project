import secrets
import string
from django.db.models import Sum, Avg # type: ignore
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


def calculate_discount_amount(order_total, discount_percentage):
    """
    Calculate the discount amount given an order total and a discount percentage.

    Args:
        order_total (int|float|Decimal): The total amount of the order.
        discount_percentage (int|float|Decimal): The discount percentage to apply.

    Returns:
        Decimal: The calculated discount amount.

    Raises:
        ValueError: If either input is not numeric or if a value is negative.

    Example:
        calculate_discount_amount(100, 15)
        # Returns Decimal('15.00')
    """
    from decimal import Decimal, InvalidOperation

    try:
        total = Decimal(str(order_total))
        percentage = Decimal(str(discount_percentage))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("order_total and discount_percentage must be numeric values.")

    if total < 0:
        raise ValueError("order_total cannot be negative.")
    if percentage < 0:
        raise ValueError("discount_percentage cannot be negative.")

    return (total * percentage) / Decimal('100')


def calculate_average_rating(review_queryset):
    """
    Calculate the average rating for a queryset of review objects.

    Args:
        review_queryset: A Django QuerySet of objects with a numeric 'rating' field.

    Returns:
        float: The average rating, or 0.0 when the queryset contains no reviews.

    Raises:
        ValueError: If the provided input is not a valid queryset.
    """
    if review_queryset is None:
        raise ValueError('A review queryset must be provided.')

    if not hasattr(review_queryset, 'aggregate'):
        raise ValueError('Input must be a Django QuerySet.')

    try:
        aggregation = review_queryset.aggregate(avg_rating=Avg('rating'))
    except Exception as exc:
        raise ValueError('Could not calculate average rating from the provided queryset.') from exc

    avg_rating = aggregation.get('avg_rating')
    return float(avg_rating) if avg_rating is not None else 0.0


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


def update_order_status(order_id, new_status):
    """
    Updates the status of an order given its ID and new status.
    
    Args:
        order_id (int): The ID of the order to update.
        new_status (str): The new status to set for the order.
    
    Returns:
        bool: True if the update was successful, False otherwise.
    
    Raises:
        ValueError: If the order is not found or status is invalid.
    """
    from .models import Order
    
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        logger.error(f"Order with ID {order_id} not found.")
        raise ValueError(f"Order with ID {order_id} not found.")
    
    # Validate status
    valid_statuses = ['pending', 'processing', 'delivered', 'cancelled']
    if new_status not in valid_statuses:
        logger.error(f"Invalid status '{new_status}' for order {order_id}. Valid statuses: {valid_statuses}")
        raise ValueError(f"Invalid status '{new_status}'. Must be one of: {valid_statuses}")
    
    old_status = order.status
    order.status = new_status
    order.save(update_fields=['status', 'updated_at'])
    
    logger.info(f"Order {order_id} status updated from '{old_status}' to '{new_status}'.")
    return True


def calculate_order_total(order_items):
    """
    Calculates the total price of an order based on a list of order items.
    
    Each order item should be a dictionary or object with 'quantity' and 'price' keys/attributes.
    
    Args:
        order_items (list): A list of order items, where each item has 'quantity' and 'price'.
    
    Returns:
        Decimal: The total cost of the order. Returns 0.00 if the list is empty.
    
    Raises:
        ValueError: If an item is missing 'quantity' or 'price', or if they are invalid types.
    
    Example:
        items = [
            {'quantity': 2, 'price': Decimal('10.50')},
            {'quantity': 1, 'price': Decimal('5.25')}
        ]
        total = calculate_order_total(items)  # Returns Decimal('26.25')
    """
    from decimal import Decimal, InvalidOperation
    
    if not order_items:
        return Decimal('0.00')
    
    total = Decimal('0.00')
    
    for item in order_items:
        # Validate that item has required fields
        if not hasattr(item, 'get') and not hasattr(item, '__getitem__'):
            raise ValueError("Order items must be dictionaries or objects with quantity and price attributes.")
        
        # Get quantity and price, handling both dict and object access
        try:
            if hasattr(item, 'get'):  # dict-like
                quantity = item.get('quantity')
                price = item.get('price')
            else:  # object-like
                quantity = getattr(item, 'quantity', None)
                price = getattr(item, 'price', None)
        except (KeyError, AttributeError):
            raise ValueError("Each order item must have 'quantity' and 'price' fields.")
        
        # Validate quantity
        if quantity is None:
            raise ValueError("Order item is missing 'quantity'.")
        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("Quantity cannot be negative.")
        except (TypeError, ValueError):
            raise ValueError("Quantity must be a non-negative integer.")
        
        # Validate price
        if price is None:
            raise ValueError("Order item is missing 'price'.")
        try:
            price = Decimal(str(price))  # Convert to string first to handle various numeric types
            if price < 0:
                raise ValueError("Price cannot be negative.")
        except (InvalidOperation, ValueError):
            raise ValueError("Price must be a valid decimal number.")
        
        # Add to total
        total += price * quantity
    
    return total         