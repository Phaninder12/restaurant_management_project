from datetime import datetime
import datetime as dt # using an alias to avoid name conflict
import re
from .models import MenuItem, Cuisine,UserReview


def calculate_discount(original_price, discount_percentage):
    """
    Calculate the discounted price given the original price and discount percentage.

    Args:
        original_price (float or int): The original price of the item.
        discount_percentage (float or int): The discount percentage (0-100).

    Returns:
        float or None: The discounted price if valid inputs, otherwise None.
    """
    try:
        # Convert to float for consistency
        price = float(original_price)
        discount = float(discount_percentage)

        # Validate inputs
        if price < 0:
            return None  # Invalid: negative price
        if discount < 0 or discount > 100:
            return None  # Invalid: discount out of range

        # Calculate discounted price
        if discount == 0:
            return price
        elif discount == 100:
            return 0.0
        else:
            discounted_price = price * (1 - discount / 100)
            return round(discounted_price, 2)

    except (ValueError, TypeError):
        # Handle cases where inputs cannot be converted to float
        return None


def is_restaurant_open():
    # Get current time
    now = datetime.now()
    current_time = now.time()
    current_day = now.weekday() 

    # Weekdays (0-4): 9 AM - 10 PM
    if current_day <= 4:
        opening = dt.time(9, 0)
        closing = dt.time(22, 0)
    # Weekends (5-6): 11 AM - 11 PM
    else:
        opening = dt.time(11, 0)
        closing = dt.time(23, 0)

    return opening <= current_time <= closing


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