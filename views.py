from rest_framework import viewsets, filters,permissions,status # type: ignore
from rest_framework.pagination import PageNumberPagination # type: ignore
from .models import Item,MenuItem
from rest_framework.response import Response # type: ignore   
from .serializers import MenuItemSerializer,ItemSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    pagination_class = StandardResultsSetPagination
    
    # Configure the search backend
    filter_backends = [filters.SearchFilter]
    # This specifies which fields to search; 'item_name' maps to your model
    search_fields = ['item_name']

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    # Restrict access to authenticated admins for write operations
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'create']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    # Explicitly handling the update logic (DRF does this automatically, 
    # but here is how you customize the response or catch exceptions)
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred during update.", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )    