from django.conf import settings
from django.shortcuts import render, redirect,get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, pagination, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response 
from rest_framework.views import APIView # type: ignore
from rest_framework.decorators import api_view # type: ignore

from .models import Order, OrderStatus, PaymentMethod, Coupon
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer, 
    OrderDetailSerializer, 
    PaymentMethodSerializer, 
    OrderStatusUpdateSerializer, 
    OrderHistorySerializer,
    ApplyCouponSerializer,
    OrderSummarySerializer
)
from .utils import is_valid_email, send_email

# --- PAGINATION ---
class OrderHistoryPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# --- API VIEWS ---

class OrderHistoryListView(generics.ListAPIView):
    """Retrieves authenticated user's order history with filtering/searching."""
    serializer_class = OrderHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OrderHistoryPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['order_id', 'customer__username']
    ordering_fields = ['created_at', 'final_price']

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')


class OrderDetailAPIView(generics.RetrieveAPIView):
    """Retrieve details of a single order; DELETE cancels the order."""
    serializer_class = OrderDetailSerializer
    permission_classes = [AllowAny] # Set to AllowAny temporarily for easier testing

    def get_queryset(self):
        return Order.objects.all()

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        order.status = 'Cancelled'
        order.save(update_fields=['status', 'updated_at'])
        return Response({"message": "Order cancelled"}, status=status.HTTP_200_OK)


class OrderStatusUpdateView(generics.UpdateAPIView):
    """Updates order status and triggers email notification."""
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        instance = serializer.save()
        customer_email = instance.customer.email
        order_id = instance.order_id or instance.id
        
        messages = {
            'Processing': "Good news! The kitchen has started preparing your meal.",
            'Shipped': "Your order is on the way!",
            'Delivered': "Enjoy your meal!",
            'Cancelled': "We're sorry, your order has been cancelled."
        }
        body = messages.get(instance.status, f"Your order status is now: {instance.status}")
        
        if is_valid_email(customer_email):
            send_email(customer_email, f"Update on Order #{order_id}", body)


class ApplyCouponView(APIView):
    """Validates and applies a coupon to an existing order globally."""
    permission_classes = [AllowAny] 

    def post(self, request, pk):
        # 1. Look for the order globally to avoid the 'Not Found' error
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"error": f"Order ID {pk} not found in database."}, status=status.HTTP_404_NOT_FOUND)

        # 2. Validate the input code
        serializer = ApplyCouponSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        code = serializer.validated_data['coupon_code']

        # 3. Validate coupon existence
        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            return Response({"error": f"Coupon code '{code}' does not exist in Admin."}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Check active/date validity
        today = timezone.now().date()
        if not coupon.is_active or \
           (coupon.valid_from and today < coupon.valid_from) or \
           (coupon.valid_until and today > coupon.valid_until):
            return Response({"error": "This coupon is currently inactive or expired."}, status=status.HTTP_400_BAD_REQUEST)

        # 5. Apply, Save, and Recalculate
        order.applied_coupon = coupon
        order.save()
        order.calculate_total()

        return Response({
            "message": "Coupon applied successfully!",
            "order_id": order.order_id,
            "discount_applied": order.discount_amount,
            "new_total": order.final_price
        }, status=status.HTTP_200_OK)


class OrderStatusRetrieveView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'order_id'

class PaymentMethodListView(generics.ListAPIView):
    serializer_class = PaymentMethodSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        return PaymentMethod.objects.filter(is_active=True)

@api_view(['POST'])
def place_order(request):
    serializer = OrderCreateSerializer(data=request.data)
    if serializer.is_valid():
        order = serializer.save(customer=request.user)
        return Response({
            "message": "Order placed successfully!",
            "order_id": order.order_id,
            "final_price": order.final_price
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class KitchenDashboardView(generics.ListAPIView):
    """
    A dedicated view for kitchen staff to see all active orders 
    that need to be prepared.
    """
    serializer_class = OrderHistorySerializer
    permission_classes = [IsAuthenticated] # Or IsAdminUser

    def get_queryset(self):
        # We only want orders that are being worked on
        active_statuses = ['pending', 'Processing'] 
        return Order.objects.filter(
            status__in=active_statuses
        ).order_by('created_at') # Oldest first so they cook in order
    
class OrderSummaryDetailView(APIView):
    """
    Retrieves a summary of a specific order by ID.
    """
    def get(self, request, pk):
        # get_object_or_404 automatically handles invalid IDs 
        # by returning a 404 Not Found response.
        order = get_object_or_404(Order, pk=pk)
        
        serializer = OrderSummarySerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)    