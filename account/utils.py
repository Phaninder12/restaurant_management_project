import re

def is_valid_phone_number(phone_string):
    """
    Validates a phone number string using regular expressions.
    Matches: +1 123-456-7890, 1234567890, (123) 456-7890, etc.
    """
    # Regex breakdown:
    # ^(\+?\d{1,3})?          -> Optional country code (e.g., +1 or 91)
    # [ \-\.]?                -> Optional separator (space, hyphen, or dot)
    # \(?\d{3}\)?             -> 3 digits, optionally wrapped in parentheses
    # [ \-\.]?\d{3}           -> 3 digits with optional separator
    # [ \-\.]?\d{4}$          -> 4 digits at the end
    
    pattern = r'^(\+?\d{1,3})?[ \-\.]?\(?\d{3}\)?[ \-\.]?\d{3}[ \-\.]?\d{4}$'
    
    # Use re.match to check the string against the pattern
    if re.match(pattern, phone_string):
        return True
    return False

