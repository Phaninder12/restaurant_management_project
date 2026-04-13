from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AvailableTablesAPIView,
    DailySpecialsView,
    MenuCategoryViewSet,
    MenuItemReviewsView,
    TableDetailView,
    MenuItemListView,
    RestaurantInfoAPIView,
    ContactFormSubmissionCreateAPIView,
    UserReviewCreateView,
    update_menu_item_availability,
    get_restaurant_info,
)

router = DefaultRouter()
router.register(r'menu-categories', MenuCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('reviews/', UserReviewCreateView.as_view(), name='create-review'),
    path('menu-items/<int:menu_item_id>/reviews/', MenuItemReviewsView.as_view(), name='menu-item-reviews'),
    path('menu-items/<int:menu_item_id>/availability/', update_menu_item_availability, name='update-menu-item-availability'),
    path('daily-specials/', DailySpecialsView.as_view(), name='daily-specials'),
    path('restaurant-info/', get_restaurant_info, name='restaurant-info'),
    # Detail endpoint: e.g., /api/tables/1/
    path('api/tables/<int:pk>/', TableDetailView.as_view(), name='table-detail'),
    path('api/menu/', MenuItemListView.as_view(), name='menu-item-list'),
    path('api/tables/available/', AvailableTablesAPIView.as_view(), name='available_tables_api'),
    path('contact/', ContactFormSubmissionCreateAPIView.as_view(), name='contact-form-submit'),
]