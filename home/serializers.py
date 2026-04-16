from rest_framework import serializers
from .models import FAQ, MenuCategory, MenuItem, Ingredient, Table, Restaurant, ContactFormSubmission, UserReview, DailyOperatingHours,MenuItem


class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'description']


class MenuCategoryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ['name']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'is_allergen']


class MenuItemSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    cuisine_name = serializers.CharField(source='cuisine.name', read_only=True)
    image = serializers.URLField(source='image_url', read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'image', 'category', 'category_name', 'cuisine', 'cuisine_name', 'ingredients', 'is_daily_special', 'is_available', 'discount_percentage']


class MenuItemIngredientsSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'ingredients']


class MenuItemAvailabilitySerializer(serializers.Serializer):
    is_available = serializers.BooleanField()

    def validate_is_available(self, value):
        if not isinstance(value, bool):
            raise serializers.ValidationError("is_available must be a boolean value.")
        return value


class MenuItemSearchSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for search results containing essential menu item details.
    """
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'description', 'is_available']


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'number', 'capacity', 'is_available']


class DailyOperatingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyOperatingHours
        fields = ['day', 'open_time', 'close_time']


class RestaurantSerializer(serializers.ModelSerializer):
    operating_hours = DailyOperatingHoursSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'phone_number', 'has_delivery', 'operating_days', 'operating_hours']


class ContactFormSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactFormSubmission
        fields = ['id', 'name', 'email', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = UserReview
        fields = ['id', 'user_name',  'rating', 'comment', 'review_date']
        read_only_fields = ['id', 'review_date']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'is_available']    

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer']