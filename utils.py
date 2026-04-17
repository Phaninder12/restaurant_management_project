from datetime import datetime
import datetime as dt # using an alias to avoid name conflict
import re
from .models import MenuItem, Cuisine, Table,UserReview


def calculate_discount(original_price, discount_percentage):
    """
    Calculate the discounted price given the original price and discount percentage.

    Args:
        original_price (float or int): The original price of the item.
        discount_percentage (float or int): The discount percentage (0-100).

    Returns:
        float or None: The discounted price rounded to 2 decimal places, 
                       or None if inputs are invalid.
    """
    try:
        # Step 3: Handle potential errors by converting to float
        price = float(original_price)
        discount = float(discount_percentage)

        # Validate logic: price cannot be negative, discount must be 0-100
        if price < 0 or discount < 0 or discount > 100:
            return None

        # Calculate discounted price
        if discount == 0:
            return round(price, 2)
        
        discount_amount = price * (discount / 100)
        discounted_price = price - discount_amount
        
        return round(discounted_price, 2)

    except (ValueError, TypeError):
        # Gracefully handle cases where inputs are strings or None
        return None


def is_restaurant_open():
    """
    Checks if the restaurant is currently open based on hardcoded hours:
    Monday - Friday: 9:00 AM to 10:00 PM
    Saturday - Sunday: Closed
    """
    # Get current day of week (0 = Monday, 6 = Sunday) and current time
    now = datetime.now()
    current_day = now.weekday() 
    current_time = now.time()

    # Define our operating windows
    opening_time = datetime.strptime("09:00", "%H:%M").time()
    closing_time = datetime.strptime("22:00", "%H:%M").time()

    # Weekdays are 0 through 4
    if 0 <= current_day <= 4:
        if opening_time <= current_time <= closing_time:
            return True
    
    # If it's the weekend or outside hours
    return False


def get_distinct_cuisines():
    """
    Retrieve a list of all unique cuisine types currently available across menu items.
    
    Returns:
        list: A list of strings, each representing a unique cuisine name.
    """
    return list(MenuItem.objects.filter(cuisine__isnull=False).values_list('cuisine__name', flat=True).distinct())


def validate_email(email):
    """
    Validate an email address using a regular expression.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    if not isinstance(email, str):
        return False
    
    # Regular expression for email validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    return re.match(email_regex, email) is not None

def calculate_average_rating(reviews):
    """
    Calculates the average rating from a QuerySet of UserReview objects.
    """
    # 1. Error handling: check if reviews exist
    count = reviews.count()
    if count == 0:
        return 0.0

    # 2. Iterate and sum
    total_rating_sum = 0
    for review in reviews:
        total_rating_sum += review.rating

    # 3. Return as float
    return float(total_rating_sum / count)

def get_available_tables_by_capacity(num_guests):
    """
    Finds all tables that are currently available and can seat 
    at least the specified number of guests.
    
    Args:
        num_guests (int): The number of people in the party.
        
    Returns:
        QuerySet: A filtered list of Table objects.
    """
    # Filter for availability AND capacity >= num_guests
    # We use __gte for "greater than or equal to"
    available_tables = Table.objects.filter(
        is_available=True, 
        capacity__gte=num_guests
    )
    
    return available_tables