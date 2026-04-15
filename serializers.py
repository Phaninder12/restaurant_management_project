from rest_framework import serializers # type: ignore
from .models import Order, OrderItem, PaymentMethod


class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.item_name')

    class Meta:
        model = OrderItem
        fields = ['item_name', 'quantity', 'price_at_time', 'get_cost']


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.username')
    status = serializers.CharField(read_only=True)
    # This calls the get_total_item_count method from your model
    total_items = serializers.ReadOnlyField(source='get_total_item_count')

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'customer_name', 'created_at', 
            'total_price', 'discount_amount', 'final_price', 
            'status', 'total_items'
        ]


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

class OrderHistorySerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    # Added here as well for the History view
    total_items = serializers.ReadOnlyField(source='get_total_item_count')

    class Meta:
        model = Order
        fields = [
            'order_id', 'created_at', 'status', 'total_price', 
            'discount_amount', 'final_price', 'total_items', 'items'
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(child=serializers.DictField(), write_only=True)

    class Meta:
        model = Order
        fields = ['items', 'applied_coupon']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            from products.models import Item
            # 1. Fetch the official item from the database
            product_item = Item.objects.get(id=item_data['item'])
            
            # 2. Create the OrderItem using the OFFICIAL price, ignoring the request data
            OrderItem.objects.create(
                order=order,
                item=product_item,
                quantity=item_data.get('quantity', 1),
                price_at_time=product_item.item_price # Force the price from our DB
            )
        
        # 3. Finalize calculations
        order.calculate_total()
        return order
    
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']    