from rest_framework import generics # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from .models import Order
from .serializers import OrderSerializer
from django.shortcuts import render, redirect # type: ignore
from .utils import is_valid_email 

# 1. This is a Class-Based View for your API
class OrderHistoryListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # This restricts the results to the currently logged-in user
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

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
        return redirect('order_success')

    return render(request, 'orders/checkout.html')