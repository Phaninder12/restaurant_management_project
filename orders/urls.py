from django.urls import path
from .views import *

urlpatterns = [
  path('history/', OrderHistoryListView.as_view(), name='order-history'),
  path('<int:pk>/', OrderDetailAPIView.as_view(), name='order_detail_api'),
  path('<str:order_id>/status/', OrderStatusRetrieveView.as_view(), name='order-status-retrieve'),
  path('<int:pk>/status/update/', OrderStatusUpdateView.as_view(), name='order-status-update'),
  path('<int:order_id>/status/get/', get_order_status, name='get-order-status'),
  path('payment-methods/', PaymentMethodListView.as_view(), name='payment-methods'),
]