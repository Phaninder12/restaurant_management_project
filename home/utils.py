from datetime import datetime
from .models import DailyOperatingHours

def get_today_operating_hours():
    """
    Returns the opening and closing times for the current day of the week.
    Returns: (open_time, close_time) or (None, None) if not found.
    """
    # 1. Get the current day of the week (e.g., 'Monday', 'Tuesday')
    current_day = datetime.now().strftime('%A')

    try:
        # 2. Query the model for the current day's entry
        # We use .get() because days should be unique in this model
        hours_entry = DailyOperatingHours.objects.get(day=current_day)
        
        # 3. Return the tuple of times
        return (hours_entry.open_time, hours_entry.close_time)
        
    except DailyOperatingHours.DoesNotExist:
        # 4. Return (None, None) if the day is missing or restaurant is closed
        return (None, None)                   