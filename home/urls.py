from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AvailableTablesAPIView,
    MenuCategoryViewSet,
    TableDetailView,
    MenuItemListView,
    RestaurantInfoAPIView,
    ContactFormSubmissionCreateAPIView,
)

router = DefaultRouter()
router.register(r'menu-categories', MenuCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('restaurant-info/', RestaurantInfoAPIView.as_view(), name='restaurant-info'),
    # Detail endpoint: e.g., /api/tables/1/
    path('api/tables/<int:pk>/', TableDetailView.as_view(), name='table-detail'),
    path('api/menu/', MenuItemListView.as_view(), name='menu-item-list'),
    path('api/tables/available/', AvailableTablesAPIView.as_view(), name='available_tables_api'),
    path('contact/', ContactFormSubmissionCreateAPIView.as_view(), name='contact-form-submit'),
]