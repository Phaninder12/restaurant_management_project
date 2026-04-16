from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
# Assuming your Order model is in home.models
# (Update the import path if your Order model is in a different app)
from .models import Order 

@receiver(post_save, sender=Order)
def notify_admin_order_status_change(sender, instance, created, **kwargs):
    """
    Signal receiver that sends an email when an order status is updated.
    """
    # 'created' is True if a new record is made. 
    # Usually, status changes happen on existing orders (created=False).
    if not created:
        subject = f"Order #{instance.id} Status Updated"
        message = f"The status of Order #{instance.id} has been changed to: {instance.status}."
        from_email = settings.DEFAULT_FROM_EMAIL
        admin_email = [settings.ADMIN_EMAIL]  # Ensure this is in your settings.py

        try:
            send_mail(subject, message, from_email, admin_email, fail_silently=False)
            print(f"Notification email sent for Order {instance.id}")
        except Exception as e:
            print(f"Email failed to send: {e}")