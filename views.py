from rest_framework import generics, status, pagination,filters # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.decorators import api_view # type: ignore
from django.shortcuts import render, redirect # type: ignore
from django_filters.rest_framework import DjangoFilterBackend # type: ignore

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


class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        # 1. Save the updated order
        instance = serializer.save()

        # 2. Logic to trigger notifications based on status
        customer_email = instance.customer.email  # Assumes Order has a ForeignKey to User
        order_id = instance.order_id or instance.id
        new_status = instance.status

        subject = f"Update on your Order #{order_id}"
        
        # Customize messages based on the status
        messages = {
            'Processing': "Good news! The kitchen has started preparing your meal.",
            'Shipped': "Your order is on the way! Our delivery partner has picked it up.",
            'Delivered': "Enjoy your meal! Your order has been marked as delivered.",
            'Cancelled': "We're sorry, your order has been cancelled. Contact us for details."
        }

        # Get the specific message or a default one
        body = messages.get(new_status, f"Your order status is now: {new_status}")

        # 3. Use your existing utility to send the email
        if is_valid_email(customer_email):
            success, msg = send_email(customer_email, subject, body)
            if not success:
                # Log the error but don't stop the API response
                print(f"Failed to notify customer for Order {order_id}: {msg}")
    """
    Update the status of an order. 
    Accepts PUT or PATCH requests.
    """
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated] # Consider IsAdminUser for actual production

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Optional: Add a custom message to the response
        return Response({
            'message': f'Order status updated to {response.data.get("status")}',
            'data': response.data
        }, status=status.HTTP_200_OK)
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