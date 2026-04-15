from django.urls import path
from . import views

urlpatterns = [
    # Collection Views
    path('history/', views.OrderHistoryListView.as_view(), name='order-history'),
    path('payment-methods/', views.PaymentMethodListView.as_view(), name='payment-methods'),
    path('place-order/', views.place_order, name='place_order'),

    # Individual Order Detail/Actions
    path('<int:pk>/', views.OrderDetailAPIView.as_view(), name='order_detail_api'),
    path('<int:pk>/status/update/', views.OrderStatusUpdateView.as_view(), name='order-status-update'),
    
    # Tracking (Public or Specific)
    path('<str:order_id>/status/', views.OrderStatusRetrieveView.as_view(), name='order-status-retrieve'),
    path('<int:order_id>/status/get/', views.get_order_status, name='get-order-status'),
]