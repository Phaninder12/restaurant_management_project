from rest_framework.generics import ListAPIView # type: ignore
from .models import MenuCategory
from products.models import Item  # Changed MenuItem to Item
from .serializers import MenuCategorySerializer, MenuItemSerializer  # Changed MenuItemSerializer to ItemSerializer

# Existing view for categories
class MenuCategoryListView(ListAPIView):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer

# New view for featured items
class FeaturedMenuItemView(ListAPIView):
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        # Using Item model and filtering by is_featured
        return Item.objects.filter(is_featured=True)  