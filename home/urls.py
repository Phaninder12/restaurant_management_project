from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AvailableMenuItemsView,
    AvailableTablesAPIView,
    DailySpecialsView,
    MenuCategoryViewSet,
    MenuCategoryNameListView,
    MenuItemReviewsView,
    TableDetailView,
    MenuItemListView,
    MenuItemDetailView,
    MenuItemPriceRangeView,
    RestaurantReviewListView,
    RestaurantInfoAPIView,
    ContactFormSubmissionCreateAPIView,
    UserReviewCreateView,
    UserReviewListView,
    RestaurantOpeningHoursListView,
    MenuItemSearchView,
    update_menu_item_availability,
    get_restaurant_info,
    get_restaurant_opening_hours,
    get_menu_item_availability,
)

router = DefaultRouter()
router.register(r'menu-categories', MenuCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('reviews/', UserReviewListView.as_view(), name='user-reviews-list'),
    path('restaurant-reviews/', RestaurantReviewListView.as_view(), name='restaurant-reviews-list'),
    path('reviews/create/', UserReviewCreateView.as_view(), name='create-review'),
    path('menu-items/', MenuItemListView.as_view(), name='menu-item-list'),
    path('menu-items/price-range/', MenuItemPriceRangeView.as_view(), name='menu-item-price-range'),
    path('menu-items/<int:menu_item_id>/', MenuItemDetailView.as_view(), name='menu-item-detail'),
    path('menu-items/<int:menu_item_id>/reviews/', MenuItemReviewsView.as_view(), name='menu-item-reviews'),
    path('menu-items/<int:menu_item_id>/availability/', update_menu_item_availability, name='update-menu-item-availability'),
    path('menu-items/<int:menu_item_id>/availability-check/', get_menu_item_availability, name='menu-item-availability-check'),
    path('menu-items/search/', MenuItemSearchView.as_view(), name='menu-item-search'),
    path('menu-categories/names/', MenuCategoryNameListView.as_view(), name='menu-category-names'),
    path('daily-specials/', DailySpecialsView.as_view(), name='daily-specials'),
    path('restaurant-info/', get_restaurant_info, name='restaurant-info'),
    path('restaurant-opening-hours/', get_restaurant_opening_hours, name='restaurant-opening-hours'),
    path('opening-hours/', RestaurantOpeningHoursListView.as_view(), name='opening-hours'),
    # Detail endpoint: e.g., /api/tables/1/
    path('tables/<int:pk>/', TableDetailView.as_view(), name='table-detail'),
    path('tables/available/', AvailableTablesAPIView.as_view(), name='available_tables_api'),
    path('contact/', ContactFormSubmissionCreateAPIView.as_view(), name='contact-form-submit'),
    path('api/available-menu/', AvailableMenuItemsView.as_view(), name='available-menu'),
]