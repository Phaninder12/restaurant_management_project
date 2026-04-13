from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.item_name')

    class Meta:
        model = OrderItem
        fields = ['item_name', 'quantity', 'price_at_time']


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.username')
    status = serializers.ReadOnlyField(source='status.name')

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'customer_name', 'created_at', 'total_price', 'discount_amount', 'final_price', 'status']


class OrderDetailSerializer(OrderSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta(OrderSerializer.Meta):
        model = Order
        fields = OrderSerializer.Meta.fields + ['items', 'applied_coupon']
