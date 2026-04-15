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
            Q(status='Pending') | Q(status='Processing')
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
    
    order_id = models.CharField(max_length=12, unique=True,  null=True, blank=True)
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
        default='Pending',  # Fixed: Match case
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
        # Fixed: Match choice case
        result = cls.objects.filter(status__in=['Completed', 'Delivered']).aggregate(total=Sum('final_price'))
        return result['total'] or Decimal('0.00')

    def calculate_prices(self):
        return self.calculate_total()

    def calculate_total(self):
        from .utils import calculate_discount
        total = sum(item.get_cost() for item in self.items.all())
        self.total_price = Decimal(total)
        self.discount_amount = calculate_discount(self)
        self.final_price = self.total_price - self.discount_amount
        if self.final_price < 0:
            self.final_price = Decimal('0.00')
        
        Order.objects.filter(pk=self.pk).update(
            total_price=self.total_price,
            discount_amount=self.discount_amount,
            final_price=self.final_price
        )
        return self.final_price

    def get_total_item_count(self):
        result = self.items.aggregate(total_qty=models.Sum('quantity'))
        return result['total_qty'] or 0

    def save(self, *args, **kwargs):
        if not self.order_id:
            from .utils import generate_unique_order_id
            self.order_id = generate_unique_order_id()
        super().save(*args, **kwargs)

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
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('order', 'item')

    def __str__(self):
        return f"{self.quantity} x {self.item.item_name if self.item else 'Unknown item'}"

    def get_cost(self):
        return (self.price_at_time or 0) * self.quantity

    def save(self, *args, **kwargs):
        if not self.price_at_time and self.item:
            self.price_at_time = self.item.item_price
        super().save(*args, **kwargs)