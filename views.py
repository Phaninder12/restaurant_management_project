from django.shortcuts import render
from rest_framework import generics
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import MenuCategory, MenuItem, Table, Restaurant
from .serializers import (
    MenuCategorySerializer,
    MenuItemSerializer,
    MenuItemIngredientsSerializer,
    TableSerializer,
    RestaurantSerializer,
)


class MenuCategoryListView(ListAPIView):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer


class MenuItemIngredientsView(RetrieveAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemIngredientsSerializer


def home_page(request):
    featured_dishes = MenuItem.objects.get_top_selling_items(3)
    return render(request, 'home/index.html', {'featured_dishes': featured_dishes})


class TableDetailView(RetrieveAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer


class RestaurantInfoAPIView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer


class MenuItemListView(generics.ListAPIView):
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        return MenuItem.objects.all()


class AvailableTablesAPIView(generics.ListAPIView):
    serializer_class = TableSerializer

    def get_queryset(self):
        return Table.objects.filter(is_available=True)
       