from django.conf import settings # type: ignore
from django.db import models # type: ignore
from django.db.models import Q # type: ignore
from decimal import Decimal
from products.models import Item


class OrderStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Order Statuses"

    def __str__(self):
        return self.name


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField(auto_now_add=False, null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.code


class OrderManager(models.Manager):
    def get_active_orders(self):
        return self.filter(
            Q(status__name='pending') | Q(status__name='processing')
        )


class Order(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True,
    )
    status = models.ForeignKey(
        OrderStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    applied_coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_orders',
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    final_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    def __str__(self):
        return f"Order {self.id}"

    @property
    def customer_name(self):
        return self.customer.username if self.customer else ''

    def calculate_total(self):
        """
        Iterates through the items in the order and sums their prices 
        multiplied by quantity to get a grand total.
        """
        # Sum up the cost of all related OrderItem objects
        total = sum(item.get_cost() for item in self.items.all())
        
        # Convert to Decimal to ensure precision and return
        self.total_price = Decimal(total)
        # Note: You can call self.save() here if you want to persist the total
        return self.total_price


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(
        Item,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='order_items',
    )
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('order', 'item')

    def __str__(self):
        return f"{self.quantity} x {self.item.item_name if self.item else 'Unknown item'}"

    def get_cost(self):
        """Calculates the total cost for this specific item line."""
        return self.price_at_time * self.quantity


class LoyaltyProgram(models.Model):
    name = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="The name of the loyalty tier (e.g., Silver Member)"
    )
    points_required = models.PositiveIntegerField(
        unique=True, 
        help_text="Minimum points required to reach this tier"
    )
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Percentage discount for this tier (e.g., 5.00 for 5%)"
    )
    description = models.TextField(
        blank=True, 
        help_text="Brief explanation of the benefits"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['points_required']