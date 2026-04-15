from django.shortcuts import render
from django.db import DatabaseError
from rest_framework import generics, status, serializers
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import MenuCategory, MenuItem, Table, Restaurant, ContactFormSubmission, UserReview, DailyOperatingHours
from .serializers import (
    MenuCategorySerializer,
    MenuCategoryNameSerializer,
    MenuItemSerializer,
    MenuItemIngredientsSerializer,
    TableSerializer,
    RestaurantSerializer,
    ContactFormSubmissionSerializer,
    UserReviewSerializer,
    DailyOperatingHoursSerializer,
    MenuItemSearchSerializer,
    MenuItemSerializer,
)


class MenuCategoryViewSet(ModelViewSet):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    permission_classes = [AllowAny]


class MenuCategoryNameListView(ListAPIView):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategoryNameSerializer
    permission_classes = [AllowAny]


class MenuItemIngredientsView(RetrieveAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemIngredientsSerializer
    permission_classes = [AllowAny]


class MenuItemDetailView(RetrieveAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'
    lookup_url_kwarg = 'menu_item_id'


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


@api_view(['GET'])
def get_restaurant_info(request):
    """
    Retrieve information about the restaurant.
    """
    try:
        restaurant = Restaurant.objects.first()
        if not restaurant:
            return Response({'error': 'No restaurant information available'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurant_opening_hours(request):
    """
    Retrieve the restaurant opening hours in a simple JSON format.
    """
    try:
        restaurant = Restaurant.objects.first()
        if not restaurant:
            return Response({'error': 'No restaurant information available'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'opening_hours': restaurant.opening_hours})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class RestaurantOpeningHoursListView(generics.ListAPIView):
    """
    Retrieve all restaurant opening hours for each day of the week.
    
    Returns a list of opening hours with days and corresponding opening/closing times.
    """
    queryset = DailyOperatingHours.objects.all().order_by('id')
    serializer_class = DailyOperatingHoursSerializer
    permission_classes = [AllowAny]


class MenuItemSearchView(generics.ListAPIView):
    """
    Search for menu items by name (case-insensitive).
    
    Query Parameters:
        q (str): The search term to find menu items by name.
    
    Returns a list of matching menu items with essential details.
    """
    serializer_class = MenuItemSearchSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = MenuItem.objects.all()
        search_query = self.request.query_params.get('q', None)
        
        if search_query:
            # Case-insensitive search using __icontains
            queryset = queryset.filter(name__icontains=search_query)
        
        return queryset.order_by('name')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_menu_item_availability(request, menu_item_id):
    """
    Retrieve the availability status of a menu item by its ID.
    """
    try:
        menu_item = MenuItem.objects.get(pk=menu_item_id)
        return Response({'available': menu_item.is_available})
    except MenuItem.DoesNotExist:
        return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)


class MenuItemPriceRangeView(generics.ListAPIView):
    """
    List menu items whose price falls between min_price and max_price.

    Query Parameters:
        min_price (decimal): The minimum price.
        max_price (decimal): The maximum price.
    """
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        from decimal import Decimal, InvalidOperation

        queryset = MenuItem.objects.all().order_by('price')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if min_price is None or max_price is None:
            raise serializers.ValidationError({
                'detail': 'Both min_price and max_price query parameters are required.'
            })

        try:
            min_price_dec = Decimal(str(min_price))
            max_price_dec = Decimal(str(max_price))
        except (InvalidOperation, TypeError, ValueError):
            raise serializers.ValidationError({
                'detail': 'min_price and max_price must be valid numeric values.'
            })

        if min_price_dec < 0 or max_price_dec < 0:
            raise serializers.ValidationError({
                'detail': 'Price values cannot be negative.'
            })

        if min_price_dec > max_price_dec:
            raise serializers.ValidationError({
                'detail': 'min_price cannot be greater than max_price.'
            })

        return queryset.filter(price__gte=min_price_dec, price__lte=max_price_dec)


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


class UserReviewPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class RestaurantReviewListView(generics.ListAPIView):
    """
    List all restaurant reviews with pagination.

    Returns a paginated JSON array of reviews with rating and review text.
    """
    queryset = UserReview.objects.all().order_by('-review_date')
    serializer_class = UserReviewSerializer
    permission_classes = [AllowAny]
    pagination_class = UserReviewPagination

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except DatabaseError as exc:
            return Response(
                {'detail': 'Unable to retrieve reviews at this time. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserReviewListView(generics.ListAPIView):
    queryset = UserReview.objects.all().order_by('-review_date')
    serializer_class = UserReviewSerializer
    permission_classes = [AllowAny]
    pagination_class = UserReviewPagination

class AvailableMenuItemsView(generics.ListAPIView):
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        """
        Return only the items where is_available is True.
        """
        return MenuItem.objects.filter(is_available=True)    
       