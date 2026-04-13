import secrets
import string
# Replace 'orders.models' and 'Coupon' with your actual app and model name
from orders.models import Coupon 

def generate_coupon_code(length=10):
    """
    Generates a unique, cryptographically secure alphanumeric coupon code.
    """
    # Define the characters allowed in the coupon code
    # We use uppercase letters and digits for readability
    characters = string.ascii_uppercase + string.digits
    
    while True:
        # Generate a random string of the specified length
        code = ''.join(secrets.choice(characters) for _ in range(length))
        
        # Check if the code already exists in the database
        if not Coupon.objects.filter(code=code).exists():
            return code     