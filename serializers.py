from rest_framework import serializers
from .models import MenuCategory, MenuItem

class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ['id', 'name']

class MenuItemSerializer(serializers.ModelSerializer):
    # This displays the category name instead of just the ID number
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'is_featured', 'category', 'category_name']

class ItemSerializer(serializers.ModelSerializer): # Changed from MenuItemSerializer
    class Meta:
        model = MenuItem # Ensure this matches your model name in home/models.py
        fields = '__all__'        