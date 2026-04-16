from rest_framework import serializers # type: ignore
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='menu_item.name')

    class Meta:
        model = OrderItem # type: ignore
        fields = ['item_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order # type: ignore
        fields = ['id', 'created_at', 'total_price', 'items']           