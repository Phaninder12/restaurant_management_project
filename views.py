from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view
from .models import MenuCategory, MenuItem, Table, Restaurant, ContactFormSubmission, UserReview
from .serializers import (
    MenuCategorySerializer,
    MenuItemSerializer,
    MenuItemIngredientsSerializer,
    TableSerializer,
    RestaurantSerializer,
    ContactFormSubmissionSerializer,
    UserReviewSerializer,
)


class MenuCategoryViewSet(ModelViewSet):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    permission_classes = [AllowAny]


class MenuItemIngredientsView(RetrieveAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemIngredientsSerializer
    permission_classes = [AllowAny]


def home_page(request):
    featured_dishes = MenuItem.objects.get_top_selling_items(3)
    return render(request, 'home/index.html', {'featured_dishes': featured_dishes})


class TableDetailView(RetrieveAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [AllowAny]


class ContactFormSubmissionCreateAPIView(CreateAPIView):
    queryset = ContactFormSubmission.objects.all()
    serializer_class = ContactFormSubmissionSerializer
    permission_classes = [AllowAny]


class RestaurantInfoAPIView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny]


class MenuItemListView(generics.ListAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return MenuItem.objects.all()


class DailySpecialsView(generics.ListAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return MenuItem.objects.filter(is_daily_special=True)


class AvailableTablesAPIView(generics.ListAPIView):
    serializer_class = TableSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Table.objects.filter(is_available=True)


class UserReviewCreateView(generics.CreateAPIView):
    serializer_class = UserReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MenuItemReviewsView(generics.ListAPIView):
    serializer_class = UserReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        menu_item_id = self.kwargs['menu_item_id']
        return UserReview.objects.filter(menu_item_id=menu_item_id).order_by('-review_date')


@api_view(['PATCH'])
def update_menu_item_availability(request, menu_item_id):
    """
    Update the availability status of a menu item.
    """
    try:
        menu_item = MenuItem.objects.get(pk=menu_item_id)
    except MenuItem.DoesNotExist:
        return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = MenuItemAvailabilitySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    is_available = serializer.validated_data['is_available']
    menu_item.is_available = is_available
    menu_item.save(update_fields=['is_available', 'updated_at'])
    
    return Response({
        'message': f'Menu item availability updated to {"available" if is_available else "unavailable"}',
        'menu_item_id': menu_item_id,
        'is_available': is_available
    })
       