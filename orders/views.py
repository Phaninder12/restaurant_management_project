from rest_framework import generics, status # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny # type: ignore
from rest_framework.response import Response # type: ignore
from .models import Order, OrderStatus, PaymentMethod
from .serializers import OrderSerializer,OrderDetailSerializer, PaymentMethodSerializer
from django.shortcuts import render, redirect # type: ignore
from .utils import is_valid_email, send_email 

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
        cancelled_status, _ = OrderStatus.objects.get_or_create(name='Cancelled')
        order.status = cancelled_status
        order.save(update_fields=['status', 'updated_at'])
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentMethodListView(generics.ListAPIView):
    serializer_class = PaymentMethodSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return PaymentMethod.objects.filter(is_active=True)