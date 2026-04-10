from datetime import datetime
import datetime as dt # using an alias to avoid name conflict

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