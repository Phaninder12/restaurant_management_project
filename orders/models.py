from django.conf import settings
from django.db import models
from django.db.models import Q, Sum
from decimal import Decimal
from products.models import Item
from django.utils import timezone

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

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class OrderManager(models.Manager):
    def get_active_orders(self):
        return self.filter(
            Q(status='pending') | Q(status='processing')
        )

    def get_orders_by_status(self, status_name):
        return self.filter(status=status_name)

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Delivered', 'Delivered'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    order_id = models.CharField(max_length=12, unique=True, editable=False, null=True, blank=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    applied_coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_orders',
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    def __str__(self):
        return f"Order {self.order_id or self.id}"

    @property
    def customer_name(self):
        return self.customer.username if self.customer else ''

    @classmethod
    def calculate_total_revenue(cls):
        result = cls.objects.filter(status__in=['completed', 'delivered']).aggregate(total=Sum('final_price'))
        return result['total'] or Decimal('0.00')

    # --- Calculation & Logic Methods ---

    def calculate_prices(self):
        """Bridge method to satisfy the call from signals.py"""
        return self.calculate_total()

    def calculate_total(self):
        """Calculates prices based on items and applies discounts."""
        from .utils import calculate_discount
        
        # 1. Sum up all related OrderItems
        total = sum(item.get_cost() for item in self.items.all())
        self.total_price = Decimal(total)
        
        # 2. Calculate discount using utility
        self.discount_amount = calculate_discount(self)
        
        # 3. Calculate final price
        self.final_price = self.total_price - self.discount_amount
        if self.final_price < 0:
            self.final_price = Decimal('0.00')
        
        # 4. Save fields back to DB directly to avoid recursive signal loops
        Order.objects.filter(pk=self.pk).update(
            total_price=self.total_price,
            discount_amount=self.discount_amount,
            final_price=self.final_price
        )
        return self.final_price

    def get_total_item_count(self):
        """
        Returns the total number of individual items in the order.
        Uses database aggregation for efficiency.
        """
        result = self.items.aggregate(total_qty=models.Sum('quantity'))
        return result['total_qty'] or 0

    def save(self, *args, **kwargs):
        if not self.order_id:
            from .utils import generate_unique_order_id
            self.order_id = generate_unique_order_id()
        super().save(*args, **kwargs)

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
        return self.price_at_time * self.quantity

class LoyaltyProgram(models.Model):
    name = models.CharField(max_length=50, unique=True)
    points_required = models.PositiveIntegerField(unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['points_required']

    def __str__(self):
        return self.name
    
class ReservationManager(models.Manager):
    def get_upcoming_reservations(self):
        return self.filter(reservation_datetime__gt=timezone.now())

class Reservation(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='order_reservations'
    )
    reservation_datetime = models.DateTimeField()
    number_of_people = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ReservationManager()

    def __str__(self):
        return f"Reservation for {self.customer} on {self.reservation_datetime}"
    
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
    # Changed null=True, blank=True so the admin doesn't force you to type it
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('order', 'item')

    def __str__(self):
        return f"{self.quantity} x {self.item.item_name if self.item else 'Unknown item'}"

    def get_cost(self):
        return self.price_at_time * self.quantity

    # --- NEW AUTOMATION LOGIC ---
    def save(self, *args, **kwargs):
        """
        Automatically fetch the price from the linked Item if price_at_time is not set.
        """
        if not self.price_at_time and self.item:
            # Assuming your 'Item' model in products/models.py has a field named 'price'
            self.price_at_time = self.item.item_price
        
        super().save(*args, **kwargs)    