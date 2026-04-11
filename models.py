from django.db import models # type: ignore
from django.contrib.auth.models import User # type: ignore
from home.models import MenuItem

class OrderStatus(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Order Statuses"

    def __str__(self):
        return self.name

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    # Add default=0 here
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code

class Order(models.Model):
    # Add default=1 here (assuming your first user ID is 1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', default=1)
    status = models.ForeignKey(OrderStatus, on_delete=models.SET_NULL, null=True)
    applied_coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    @property
    def customer(self):
        return self.user.username

    @property
    def discount_amount(self):
        return self.applied_coupon.discount_amount if self.applied_coupon else 0

    @property
    def final_price(self):
        return self.total_price - self.discount_amount
    
    def get_unique_item_names(self):
        """
        Retrieves a list of unique names of all MenuItems 
        associated with this specific order.
        """
        # Since OrderItem has related_name='items', use self.items
        # We use a set comprehension for efficient uniqueness handling
        unique_names = {
            item.menu_item.name 
            for item in self.items.all()
        }
        
        return list(unique_names)

# --- THIS WAS LIKELY MISSING ---
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"
    
