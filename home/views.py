from django.shortcuts import render
from rest_framework import generics
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from .models import MenuCategory, MenuItem, Table, Restaurant, ContactFormSubmission
from .serializers import (
    MenuCategorySerializer,
    MenuItemSerializer,
    MenuItemIngredientsSerializer,
    TableSerializer,
    RestaurantSerializer,
    ContactFormSubmissionSerializer,
)


class MenuCategoryViewSet(ModelViewSet):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    permission_classes = [AllowAny]


class MenuItemIngredientsView(RetrieveAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemIngredientsSerializer
    permission_classes = [AllowAny]


def home_page(request):
    featured_dishes = MenuItem.objects.get_top_selling_items(3)
    return render(request, 'home/index.html', {'featured_dishes': featured_dishes})


class TableDetailView(RetrieveAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [AllowAny]


class ContactFormSubmissionCreateAPIView(CreateAPIView):
    queryset = ContactFormSubmission.objects.all()
    serializer_class = ContactFormSubmissionSerializer
    permission_classes = [AllowAny]


class RestaurantInfoAPIView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny]


class MenuItemListView(generics.ListAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return MenuItem.objects.all()


class AvailableTablesAPIView(generics.ListAPIView):
    serializer_class = TableSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Table.objects.filter(is_available=True)
       