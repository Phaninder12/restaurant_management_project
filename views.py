from rest_framework import generics, status # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.decorators import api_view
from .models import Order, OrderStatus, PaymentMethod
from .serializers import OrderSerializer,OrderDetailSerializer, PaymentMethodSerializer, OrderStatusUpdateSerializer
from django.shortcuts import render, redirect # type: ignore
from .utils import is_valid_email, send_email


class OrderStatusUpdateView(APIView):
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


@api_view(['GET'])
def get_order_status(request, order_id):
    """
    Retrieve the status of an order by its ID.
    """
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'order_id': order.order_id or order.id,
        'status': order.status
    }) 

# 1. This is a Class-Based View for your API
class OrderHistoryListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # This restricts the results to the currently logged-in user
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')

# 2. This is a Function-Based View for your HTML Form (Moved outside the class)
def place_order_view(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')

        # --- VALIDATION LOGIC ---
        if not is_valid_email(user_email):
            # If invalid, return the user to the form with an error message
            return render(request, 'orders/checkout.html', {
                'error': 'Please enter a valid email address.',
                'data': request.POST 
            })
        # ------------------------

        # If code reaches here, the email is valid!
        # Proceed to save the order logic here...
        
        # Example: Send a confirmation email
        subject = "Order Confirmation"
        message_body = "Thank you for your order! We have received your request and will process it shortly."
        success, msg = send_email(user_email, subject, message_body)
        if not success:
            # Handle email sending failure (e.g., log it or show a message)
            print(f"Email sending failed: {msg}")
        
        return redirect('order_success')

    return render(request, 'orders/checkout.html')

class OrderDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve details of a single order by its ID, 
    restricted to the owner of the order.
    """
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only retrieve orders they placed themselves
        return Order.objects.filter(customer=self.request.user)

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        order.status = 'cancelled'
        order.save(update_fields=['status', 'updated_at'])
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentMethodListView(generics.ListAPIView):
    serializer_class = PaymentMethodSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return PaymentMethod.objects.filter(is_active=True)


class OrderStatusUpdateView(APIView):
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