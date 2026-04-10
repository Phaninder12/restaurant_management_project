from rest_framework.generics import ListAPIView, RetrieveAPIView # type: ignore
# Import models clearly
from .models import MenuCategory, MenuItem as HomeMenuItem
from products.models import Item

# Import serializers
from .serializers import (
    MenuCategorySerializer, 
    MenuItemSerializer, 
    MenuItemIngredientsSerializer
)

# 1. Existing view for categories
class MenuCategoryListView(ListAPIView):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer

# 2. View for featured items (using products.Item)
class FeaturedMenuItemView(ListAPIView):
    serializer_class = MenuItemSerializer # Ensure this is the one from home.serializers

    def get_queryset(self):
        return Item.objects.filter(is_featured=True)

# 3. View for Ingredients (using home.MenuItem)
class MenuItemIngredientsView(RetrieveAPIView):
    # Use the 'HomeMenuItem' alias to be safe
    queryset = HomeMenuItem.objects.all()
    serializer_class = MenuItemIngredientsSerializer