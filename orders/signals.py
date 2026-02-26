from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def update_order_prices(sender, instance, created, **kwargs):
    if created:
        return  # skip on create

    instance.calculate_prices()
    instance.save(update_fields=['total_price', 'discount_amount', 'final_price'])