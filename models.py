import datetime
from django.db import models # type: ignore
from django.db.models import Count # type: ignore

class MenuCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_featured = models.BooleanField(default=False)
    # Adding the many-to-many relationship for ingredients
    ingredients = models.ManyToManyField('Ingredient', related_name="menu_items", blank=True)

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    is_allergen = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    has_delivery = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class DailySpecialManager(models.Manager):
    def upcoming(self):
        today = datetime.date.today()
        # Note: This requires the 'date' field to exist in the model
        return self.filter(date__gte=today).order_by('date')

class DailySpecial(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField(null=True, blank=True) # Ensure this matches your manager logic
    price = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

    objects = DailySpecialManager()

    @staticmethod
    def get_random_special():
        return DailySpecial.objects.filter(is_active=True).order_by('?').first()

    def __str__(self):
        return f"{self.name} ({self.date})"
    
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
    
# 1. Create the Custom Manager
class MenuItemManager(models.Manager):
    def get_top_selling_items(self, num_items=5):
        """
        Annotates each MenuItem with the count of related OrderItem instances,
        orders them by that count descending, and limits the result.
        """
        return self.get_queryset().annotate(
            order_count=Count('orderitem')  # 'orderitem' is the default related name
        ).order_by('-order_count')[:num_items]

# 2. Attach it to your Model
class MenuItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # ... other fields ...

    # Assign the custom manager
    objects = MenuItemManager()

    def __str__(self):
        return self.name    