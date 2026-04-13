from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def update_order_prices(sender, instance, created, update_fields=None, **kwargs):
    if created:
        return  # skip on create

    # Avoid infinite recursion when the signal updates the same fields.
    if update_fields and set(update_fields) <= {'total_price', 'discount_amount', 'final_price'}:
        return

    instance.calculate_prices()
    instance.save(update_fields=['total_price', 'discount_amount', 'final_price'])