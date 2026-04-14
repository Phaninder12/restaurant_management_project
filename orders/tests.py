from django.test import TestCase
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from products.models import Item
from home.models import MenuItem, UserReview
from .models import Order, OrderItem
from .utils import calculate_discount_amount, calculate_average_rating

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

    def test_calculate_discount_amount(self):
        """Tests that calculate_discount_amount returns the correct discount."""
        self.assertEqual(calculate_discount_amount(Decimal('100.00'), Decimal('15')), Decimal('15.0000'))
        self.assertEqual(calculate_discount_amount(200, 10), Decimal('20'))
        self.assertEqual(calculate_discount_amount('50.5', '20'), Decimal('10.10'))

    def test_calculate_discount_amount_invalid_inputs(self):
        """Tests invalid inputs for calculate_discount_amount."""
        with self.assertRaises(ValueError):
            calculate_discount_amount('abc', 10)
        with self.assertRaises(ValueError):
            calculate_discount_amount(100, 'xyz')
        with self.assertRaises(ValueError):
            calculate_discount_amount(-100, 10)
        with self.assertRaises(ValueError):
            calculate_discount_amount(100, -5)


class ReviewUtilityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reviewer')
        self.menu_item = MenuItem.objects.create(
            name='Test Dish',
            description='A test dish',
            price=Decimal('9.99')
        )

    def test_calculate_average_rating_with_reviews(self):
        UserReview.objects.create(
            user=self.user,
            menu_item=self.menu_item,
            rating=4,
            comment='Good'
        )
        UserReview.objects.create(
            user=self.user,
            menu_item=self.menu_item,
            rating=5,
            comment='Excellent'
        )

        avg_rating = calculate_average_rating(UserReview.objects.all())
        self.assertAlmostEqual(avg_rating, 4.5)

    def test_calculate_average_rating_empty_queryset(self):
        avg_rating = calculate_average_rating(UserReview.objects.none())
        self.assertEqual(avg_rating, 0.0)

    def test_calculate_average_rating_invalid_input(self):
        with self.assertRaises(ValueError):
            calculate_average_rating(None)


class OrderCancelAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.order = Order.objects.create(customer=self.user)
        self.url = reverse('order_detail_api', kwargs={'pk': self.order.pk})

    def test_cancel_order_updates_status(self):
        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertIsNotNone(self.order.status)
        self.assertEqual(self.order.status.name, 'Cancelled')
        self.assertEqual(response.data['status'], 'Cancelled')

    def test_cannot_cancel_other_users_order(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.client.force_login(other_user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
