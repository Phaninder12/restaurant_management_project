from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'          # ← This automatically takes id, item_name, item_price, created_at
        # OR you can write explicitly:
        # fields = ['id', 'item_name', 'item_price', 'created_at']