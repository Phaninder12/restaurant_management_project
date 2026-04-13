from django.urls import path
from .views import (
    AvailableTablesAPIView,
    MenuCategoryListView,
    TableDetailView,
    MenuItemListView,
    RestaurantInfoAPIView,
    ContactFormSubmissionCreateAPIView,
)

urlpatterns = [
    path('menu-categories/', MenuCategoryListView.as_view(), name='menu-categories'),
    path('restaurant-info/', RestaurantInfoAPIView.as_view(), name='restaurant-info'),
    # Detail endpoint: e.g., /api/tables/1/
    path('api/tables/<int:pk>/', TableDetailView.as_view(), name='table-detail'),
    path('api/menu/', MenuItemListView.as_view(), name='menu-item-list'),
    path('api/tables/available/', AvailableTablesAPIView.as_view(), name='available_tables_api'),
    path('contact/', ContactFormSubmissionCreateAPIView.as_view(), name='contact-form-submit'),
]