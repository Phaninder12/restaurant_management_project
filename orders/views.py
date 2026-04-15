from rest_framework import generics, status, pagination,filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.shortcuts import render, redirect
from django_filters.rest_framework import DjangoFilterBackend

from .models import Order, OrderStatus, PaymentMethod
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer, 
    OrderDetailSerializer, 
    PaymentMethodSerializer, 
    OrderStatusUpdateSerializer, 
    OrderHistorySerializer
)
from .utils import is_valid_email, send_email

# --- PAGINATION ---

class OrderHistoryPagination(pagination.PageNumberPagination):
    page_size = 10  # Number of orders per page
    page_size_query_param = 'page_size'
    max_page_size = 100

# --- API VIEWS ---

class OrderHistoryListView(generics.ListAPIView):
    """
    Enhanced API endpoint to retrieve, filter, and search order history.
    """
    serializer_class = OrderHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OrderHistoryPagination
    
    # Add Filter and Search backends
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Define which fields can be filtered
    filterset_fields = ['status']
    
    # Define which fields can be searched
    search_fields = ['order_id', 'customer__username']
    
    # Default ordering
    ordering_fields = ['created_at', 'final_price']

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')
    """
    API endpoint that retrieves the authenticated user's order history.
    """
    serializer_class = OrderHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OrderHistoryPagination

    def get_queryset(self):
        # Restricts the results to the currently logged-in user
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')


class OrderDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve details of a single order by its ID, 
    restricted to the owner of the order.
    """
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

    def delete(self, request, *args, **kwargs):
        """Custom delete method to 'cancel' an order rather than removing it."""
        order = self.get_object()
        order.status = 'cancelled'
        order.save(update_fields=['status', 'updated_at'])
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderStatusUpdateView(APIView):
    """
    Update the status of an order (Admin/Staff utility).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_status = serializer.validated_data['status']
        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])

        return Response({'message': f'Order status updated to {new_status}'}, status=status.HTTP_200_OK)


class OrderStatusRetrieveView(generics.RetrieveAPIView):
    """
    Retrieve order status by the unique order_id (Public tracking).
    """
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'order_id'


class PaymentMethodListView(generics.ListAPIView):
    """
    List all active payment methods.
    """
    serializer_class = PaymentMethodSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return PaymentMethod.objects.filter(is_active=True)


@api_view(['GET'])
def get_order_status(request, order_id):
    """
    Simple function-based view to retrieve order status.
    """
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'order_id': order.order_id or order.id,
        'status': order.status
    }) 

# --- TEMPLATE VIEWS (HTML) ---

def place_order_view(request):
    """
    Handles the checkout form submission for placing an order.
    """
    if request.method == 'POST':
        user_email = request.POST.get('email')

        # Validation Logic
        if not is_valid_email(user_email):
            return render(request, 'orders/checkout.html', {
                'error': 'Please enter a valid email address.',
                'data': request.POST 
            })

        # If valid, proceed to save order...
        # Example: Send confirmation email
        subject = "Order Confirmation"
        message_body = "Thank you for your order! We have received your request."
        success, msg = send_email(user_email, subject, message_body)
        
        if not success:
            print(f"Email sending failed: {msg}")
        
        return redirect('order_success')

    return render(request, 'orders/checkout.html')

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