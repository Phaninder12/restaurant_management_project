from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from datetime import date


class OrderStatus(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Status name"
    )

    class Meta:
        verbose_name = "Order Status"
        verbose_name_plural = "Order Statuses"
        ordering = ['name']

    def __str__(self):
        return self.name


class Coupon(models.Model):
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Coupon code (case-insensitive)"
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Discount in percent (0–100)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this coupon currently active?"
    )
    valid_from = models.DateField(
        default=date.today,
        help_text="Coupon becomes valid from this date"
    )
    valid_until = models.DateField(
        null=True,
        blank=True,
        help_text="Coupon expires after this date (leave empty for no expiry)"
    )

    class Meta:
        ordering = ['-valid_from']

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}%)"

    def is_valid_now(self):
        today = date.today()
        return (
            self.is_active and
            self.valid_from <= today and
            (self.valid_until is None or today <= self.valid_until)
        )


class OrderItem(models.Model):
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='items'
    )
    item = models.ForeignKey(
        'products.Item',
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price of the item when the order was placed"
    )

    class Meta:
        unique_together = [['order', 'item']]  # prevent duplicate items in same order

    def __str__(self):
        return f"{self.quantity} × {self.item.item_name if self.item else 'Item'}"

    @property
    def subtotal(self):
        return self.quantity * self.price_at_time


class Order(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Customer",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last updated")

    # These fields are computed — not set manually
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False,
        verbose_name="Subtotal (before discount)"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        editable=False,
        verbose_name="Discount applied"
    )
    final_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False,
        verbose_name="Amount to pay"
    )

    applied_coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_orders',
        verbose_name="Applied coupon"
    )
    status = models.ForeignKey(
        OrderStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name="Order status"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        if self.customer:
            return f"Order #{self.id} - {self.customer}"
        return f"Order #{self.id} (guest)"

    def calculate_prices(self):
        """Recalculate totals based on items and coupon"""
        if not self.pk:
            # New object → no items yet → safe defaults
            self.total_price = 0
            self.discount_amount = 0
            self.final_price = 0
            return

        # Only run real calculation when order exists in DB
        subtotal = sum(item.subtotal for item in self.items.all())
        self.total_price = subtotal

        discount = 0
        if self.applied_coupon and self.applied_coupon.is_valid_now():
            discount = subtotal * (self.applied_coupon.discount_percentage / 100)

        self.discount_amount = discount
        self.final_price = subtotal - discount

    def save(self, *args, **kwargs):
        self.calculate_prices()
        super().save(*args, **kwargs)