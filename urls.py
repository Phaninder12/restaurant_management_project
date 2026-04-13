from django.urls import path
from .views import *

urlpatterns = [
  path('history/', OrderHistoryListView.as_view(), name='order-history'),
  path('orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order_detail_api'),
  path('orders/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
  path('payment-methods/', PaymentMethodListView.as_view(), name='payment-methods'),
]