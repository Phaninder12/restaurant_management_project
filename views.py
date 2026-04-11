from rest_framework.generics import ListAPIView, RetrieveAPIView # type: ignore
# Import models clearly
from .models import MenuCategory, MenuItem as HomeMenuItem,Table
from products.models import Item,MenuItem


# Import serializers
from .serializers import (
    MenuCategorySerializer, 
    MenuItemSerializer, 
    MenuItemIngredientsSerializer,
    TableSerializer
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

def home_page(request):
    featured_dishes = MenuItem.objects.get_top_selling_items(3)
    return render(request, 'home/index.html', {'featured_dishes': featured_dishes})     # type: ignore

class TableDetailView(RetrieveAPIView): # type: ignore
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    # lookup_field defaults to 'pk' (primary key), which matches the URL logic