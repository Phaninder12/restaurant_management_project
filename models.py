import datetime
from django.db import models


class MenuCategory(models.Model):
    name = models.CharField(max_length=100)

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
    ingredients = models.ManyToManyField('Ingredient', related_name='menu_items', blank=True)

    objects = MenuItemManager()

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
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
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK, unique=True)
    open_time = models.TimeField()
    close_time = models.TimeField()

    def __str__(self):
        return f"{self.day}: {self.open_time} - {self.close_time}"
    