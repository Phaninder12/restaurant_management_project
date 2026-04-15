import re


def format_phone_number(phone_str):
    """
    Formats a string into a standard phone format: (XXX) XXX-XXXX
    Returns the original string if it's invalid.
    """
    try:
        # Step 1: Remove all non-numeric characters
        # e.g., "+1 (555) 123-4567" -> "15551234567"
        cleaned = re.sub(r'\D', '', str(phone_str))

        # Step 2: Handle different lengths
        if len(cleaned) == 10:
            # Format: (123) 456-7890
            return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
        
        elif len(cleaned) == 11 and cleaned.startswith('1'):
            # Format for US country code: +1 (123) 456-7890
            return f"+1 ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:]}"
        
        else:
            # If it's an unexpected length, return as is or handle specifically
            return phone_str

    except Exception as e:
        # Gracefully handle None values or unexpected types
        print(f"Error formatting phone number: {e}")
        return phone_str