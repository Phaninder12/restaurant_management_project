from rest_framework.generics import ListAPIView, RetrieveAPIView # type: ignore
# Import models clearly
from .models import MenuCategory, MenuItem as HomeMenuItem,Table,MenuItem
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

class MenuItemListView(generics.ListAPIView): # type: ignore
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned items to a given category,
        by filtering against a `category` query parameter in the URL.
        """
        queryset = MenuItem.objects.all()
        category_name = self.request.query_params.get('category')
        
        if category_name is not None:
            # We use __iexact for case-insensitive matching (e.g., 'Pizza' vs 'pizza')
            queryset = queryset.filter(category__name__iexact=category_name)
        
        return queryset    

class AvailableTablesAPIView(generics.ListAPIView): # type: ignore
    """
    API endpoint that returns a list of all tables where is_available is True.
    """
    serializer_class = TableSerializer

    def get_queryset(self):
        # Filter the queryset to only include available tables
        return Table.objects.filter(is_available=True)    