from django.test import TestCase
from decimal import Decimal
from django.contrib.auth import get_user_model
from products.models import Item
from .models import Order, OrderItem

User = get_user_model()

class OrderModelTest(TestCase):
    def setUp(self):
        # 1. Create a User for the order
        self.user = User.objects.create(username="testuser")
        
        # 2. Create items using 'item_price' as defined in your products/models.py
        self.burger = Item.objects.create(
            item_name="Burger", 
            item_price=Decimal('10.00')
        )
        self.fries = Item.objects.create(
            item_name="Fries", 
            item_price=Decimal('5.00')
        )
        
        # 3. Create the order
        self.order = Order.objects.create(customer=self.user)

    def test_calculate_total_cost(self):
        """Tests that calculate_total accurately sums all order items."""
        
        # Add 2 Burgers ($10.00 * 2 = $20.00)
        OrderItem.objects.create(
            order=self.order, 
            item=self.burger, 
            price_at_time=self.burger.item_price, 
            quantity=2
        )
        
        # Add 1 Fries ($5.00 * 1 = $5.00)
        OrderItem.objects.create(
            order=self.order, 
            item=self.fries, 
            price_at_time=self.fries.item_price, 
            quantity=1
        )

        # Expected: 20.00 + 5.00 = 25.00
        self.assertEqual(self.order.calculate_total(), Decimal('25.00'))

    def test_empty_order_total(self):
        """Tests that an order with no items returns 0."""
        empty_order = Order.objects.create(customer=self.user)
        # Using 0 as a Decimal or Integer works here, but Decimal is cleaner for money
        self.assertEqual(empty_order.calculate_total(), Decimal('0.00'))