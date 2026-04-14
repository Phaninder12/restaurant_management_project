from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AvailableTablesAPIView,
    DailySpecialsView,
    MenuCategoryViewSet,
    MenuCategoryNameListView,
    MenuItemReviewsView,
    TableDetailView,
    MenuItemListView,
    RestaurantInfoAPIView,
    ContactFormSubmissionCreateAPIView,
    UserReviewCreateView,
    UserReviewListView,
    RestaurantOpeningHoursListView,
    MenuItemSearchView,
    update_menu_item_availability,
    get_restaurant_info,
)

router = DefaultRouter()
router.register(r'menu-categories', MenuCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('reviews/', UserReviewListView.as_view(), name='user-reviews-list'),
    path('reviews/create/', UserReviewCreateView.as_view(), name='create-review'),
    path('menu-items/<int:menu_item_id>/reviews/', MenuItemReviewsView.as_view(), name='menu-item-reviews'),
    path('menu-items/<int:menu_item_id>/availability/', update_menu_item_availability, name='update-menu-item-availability'),
    path('menu-items/search/', MenuItemSearchView.as_view(), name='menu-item-search'),
    path('menu-categories/names/', MenuCategoryNameListView.as_view(), name='menu-category-names'),
    path('daily-specials/', DailySpecialsView.as_view(), name='daily-specials'),
    path('restaurant-info/', get_restaurant_info, name='restaurant-info'),
    path('opening-hours/', RestaurantOpeningHoursListView.as_view(), name='opening-hours'),
    # Detail endpoint: e.g., /api/tables/1/
    path('api/tables/<int:pk>/', TableDetailView.as_view(), name='table-detail'),
    path('api/menu/', MenuItemListView.as_view(), name='menu-item-list'),
    path('api/tables/available/', AvailableTablesAPIView.as_view(), name='available_tables_api'),
    path('contact/', ContactFormSubmissionCreateAPIView.as_view(), name='contact-form-submit'),
]