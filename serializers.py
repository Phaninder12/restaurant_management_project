from rest_framework import serializers # type: ignore
from .models import MenuCategory, MenuItem, Ingredient, Table # Added Ingredient and Table here

class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ['id', 'name']

class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'is_featured', 'category', 'category_name']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem 
        fields = '__all__'

# --- ADD THE CODE BELOW TO FIX THE ERROR ---

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'is_allergen']

class MenuItemIngredientsSerializer(serializers.ModelSerializer):
    # This nests the ingredients inside the MenuItem response
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'ingredients']

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['table_number', 'capacity', 'is_available']