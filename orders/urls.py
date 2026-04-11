from django.urls import path
from .views import AvailableTablesAPIView, MenuCategoryListView, TableDetailView,MenuItemListView

urlpatterns = [
    path('menu-categories/', MenuCategoryListView.as_view(), name='menu-categories'),
    # Detail endpoint: e.g., /api/tables/1/
    path('api/tables/<int:pk>/', TableDetailView.as_view(), name='table-detail'),
    path('api/menu/', MenuItemListView.as_view(), name='menu-item-list'),
    path('api/tables/available/', AvailableTablesAPIView.as_view(), name='available_tables_api'),
]