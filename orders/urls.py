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
    path('<int:pk>/apply-coupon/', views.ApplyCouponView.as_view(), name='apply-coupon'),
    
    # Tracking (Public tracking via the string order_id)
    path('<str:order_id>/status/', views.OrderStatusRetrieveView.as_view(), name='order-status-retrieve'),
    path('kitchen/dashboard/', views.KitchenDashboardView.as_view(), name='kitchen-dashboard'),
    path('summary/<int:pk>/', views.OrderSummaryDetailView.as_view(), name='order-summary'),
]