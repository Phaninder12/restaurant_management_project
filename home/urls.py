from django.urls import path
from .views import MenuCategoryListView, TableDetailView

urlpatterns = [
    path('menu-categories/', MenuCategoryListView.as_view(), name='menu-categories'),
    # Detail endpoint: e.g., /api/tables/1/
    path('api/tables/<int:pk>/', TableDetailView.as_view(), name='table-detail'),
]                                       