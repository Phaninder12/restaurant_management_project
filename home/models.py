import datetime
from django.db import models # type: ignore

class MenuCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=255)
    # Optional: Link MenuItem to MenuCategory
    # category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items', null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    # New Field
    has_delivery = models.BooleanField(default=False)

    def __str__(self):
        return self.name    
    
class DailySpecial(models.Model):
    # Assuming these fields exist based on standard restaurant apps
    name = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    @staticmethod
    def get_random_special():
        """
        Retrieves a single random active daily special.
        Returns None if no specials are found.
        """
        # We filter by is_active=True to ensure we don't pick an old special
        queryset = DailySpecial.objects.filter(is_active=True).order_by('?')
        
        # .first() returns the first object in the randomized queryset, 
        # or None if the queryset is empty.
        return queryset.first()

    def __str__(self):
        return self.name    
    
class DailySpecialManager(models.Manager):
    def upcoming(self):
        """
        Returns specials that are scheduled for today or later.
        """
        today = datetime.date.today()
        return self.filter(date__gte=today).order_by('date')

class DailySpecialManager(models.Manager):
    def upcoming(self):
        today = datetime.date.today()
        return self.filter(date__gte=today).order_by('date')

# 2. Add the model (or update your existing one)
class DailySpecial(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    price = models.DecimalField(max_digits=5, decimal_places=2)

    # 3. Paste this line inside the model class
    objects = DailySpecialManager()

    def __str__(self):
        return f"{self.name} ({self.date})"        