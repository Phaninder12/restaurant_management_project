import secrets
import string

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