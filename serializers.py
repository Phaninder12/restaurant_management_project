from rest_framework import serializers
from .models import MenuCategory, MenuItem, Ingredient, Table, Restaurant, ContactFormSubmission, UserReview, DailyOperatingHours


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

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'cuisine', 'ingredients', 'is_daily_special', 'is_available']


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


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'number', 'capacity', 'is_available']


class RestaurantSerializer(serializers.ModelSerializer):
    operating_hours = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'phone_number', 'has_delivery', 'operating_days', 'operating_hours']

    def get_operating_hours(self, obj):
        from .models import DailyOperatingHours
        hours = DailyOperatingHours.objects.all()
        return DailyOperatingHoursSerializer(hours, many=True).data


class DailyOperatingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyOperatingHours
        fields = ['day', 'open_time', 'close_time']


class ContactFormSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactFormSubmission
        fields = ['id', 'name', 'email', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    menu_item = serializers.ReadOnlyField(source='menu_item.name')

    class Meta:
        model = UserReview
        fields = ['id', 'user', 'menu_item', 'rating', 'comment', 'review_date']
        read_only_fields = ['id', 'review_date']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
