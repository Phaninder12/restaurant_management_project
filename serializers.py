from rest_framework import serializers
from .models import Order, OrderItem, PaymentMethod


class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.item_name')

    class Meta:
        model = OrderItem
        fields = ['item_name', 'quantity', 'price_at_time']


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.username')
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'customer_name', 'created_at', 'total_price', 'discount_amount', 'final_price', 'status']


class OrderDetailSerializer(OrderSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta(OrderSerializer.Meta):
        model = Order
        fields = OrderSerializer.Meta.fields + ['items', 'applied_coupon']


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'description', 'is_active']


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=50)

    def validate_status(self, value):
        allowed_statuses = ['pending', 'processing', 'delivered', 'cancelled']
        if value not in allowed_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return value
