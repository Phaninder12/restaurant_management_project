import datetime
from django.conf import settings
from django.db import models


class MenuCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Cuisine(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    is_allergen = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class MenuItemManager(models.Manager):
    def get_top_selling_items(self, num_items=5):
        return self.get_queryset().all()[:num_items]


class MenuItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.SET_NULL, null=True, blank=True, related_name='menu_items')
    ingredients = models.ManyToManyField('Ingredient', related_name='menu_items', blank=True)
    is_daily_special = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    objects = MenuItemManager()

    def __str__(self):
        return self.name

    def get_final_price(self):
        """
        Return the final menu item price after applying any discount.

        The discount is calculated as a percentage of the base price.
        If the configured discount is invalid or zero, the base price is returned.
        """
        from decimal import Decimal

        try:
            discount = Decimal(self.discount_percentage)
        except Exception:
            discount = Decimal('0')

        if discount <= 0:
            return float(self.price)

        if discount > 100:
            discount = Decimal('100')

        final_price = self.price * (Decimal('100') - discount) / Decimal('100')
        return float(final_price.quantize(Decimal('0.01')))


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    has_delivery = models.BooleanField(default=False)
    operating_days = models.CharField(
        max_length=100,
        default="Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        help_text="Comma-separated days of operation (e.g., Mon,Tue,Wed)"
    )

    def __str__(self):
        return self.name


class DailySpecialManager(models.Manager):
    def upcoming(self):
        today = datetime.date.today()
        return self.filter(date__gte=today).order_by('date')


class DailySpecial(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField(null=True, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

    objects = DailySpecialManager()


class Table(models.Model):
    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Table {self.number}"


class DailyOperatingHours(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='operating_hours')
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    open_time = models.TimeField()
    close_time = models.TimeField()

    class Meta:
        unique_together = ('restaurant', 'day')

    def __str__(self):
        return f"{self.restaurant.name} - {self.day}: {self.open_time} - {self.close_time}"


class ContactFormSubmission(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ContactFormSubmission from {self.name} <{self.email}>"


class UserReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.menu_item.name}: {self.rating}/5"


class LoyaltyProgram(models.Model):
    name = models.CharField(max_length=100, unique=True)
    points_per_dollar_spent = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations', null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations')
    reservation_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    party_size = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['reservation_date', 'start_time']

    def __str__(self):
        return f"Reservation on {self.reservation_date} from {self.start_time} to {self.end_time}"

    @classmethod
    def find_available_slots(cls, reservation_date, start_time, end_time, table_id=None, slot_length_minutes=30):
        """
        Find available reservation slots for a date/time range.

        Args:
            reservation_date (datetime.date): The date to search.
            start_time (datetime.time or str): The earliest slot start time.
            end_time (datetime.time or str): The latest slot end time.
            table_id (int, optional): Restrict availability to a particular table.
            slot_length_minutes (int): Length of each slot in minutes.

        Returns:
            list[dict]: Available slots as dictionaries with 'start' and 'end' times.
        """
        if isinstance(start_time, str):
            start_time = datetime.datetime.strptime(start_time, '%H:%M').time()
        if isinstance(end_time, str):
            end_time = datetime.datetime.strptime(end_time, '%H:%M').time()

        if start_time >= end_time:
            raise ValueError('start_time must be before end_time')

        queryset = cls.objects.filter(reservation_date=reservation_date)
        if table_id is not None:
            queryset = queryset.filter(table_id=table_id)

        overlapping_reservations = queryset.filter(
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).order_by('start_time')

        # Build a timeline of occupied intervals.
        occupied = []
        for reservation in overlapping_reservations:
            occupied_start = max(reservation.start_time, start_time)
            occupied_end = min(reservation.end_time, end_time)
            if occupied_start < occupied_end:
                occupied.append((occupied_start, occupied_end))

        available_slots = []
        current_start = datetime.datetime.combine(datetime.date.min, start_time)
        range_end = datetime.datetime.combine(datetime.date.min, end_time)

        for occupied_start, occupied_end in occupied:
            occupied_dt_start = datetime.datetime.combine(datetime.date.min, occupied_start)
            occupied_dt_end = datetime.datetime.combine(datetime.date.min, occupied_end)

            if current_start + datetime.timedelta(minutes=slot_length_minutes) <= occupied_dt_start:
                slot_end = occupied_dt_start
                available_slots.extend(cls._split_time_range(current_start, slot_end, slot_length_minutes))

            current_start = max(current_start, occupied_dt_end)
            if current_start >= range_end:
                break

        if current_start + datetime.timedelta(minutes=slot_length_minutes) <= range_end:
            available_slots.extend(cls._split_time_range(current_start, range_end, slot_length_minutes))

        return available_slots

    @staticmethod
    def _split_time_range(start_dt, end_dt, slot_length_minutes):
        slots = []
        while start_dt + datetime.timedelta(minutes=slot_length_minutes) <= end_dt:
            slot_end = start_dt + datetime.timedelta(minutes=slot_length_minutes)
            slots.append({
                'start': start_dt.time().strftime('%H:%M'),
                'end': slot_end.time().strftime('%H:%M'),
            })
            start_dt = slot_end
        return slots
    