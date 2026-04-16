from django.contrib import admin # type: ignore
from .models import Ingredient, Restaurant,MenuItem, MenuCategory, Cuisine, Table, UserReview

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available']
    list_filter = ['is_available', 'category']
    # Add the action name here
    actions = ['make_unavailable', 'make_available']

    @admin.action(description="Mark selected items as Out of Stock")
    def make_unavailable(self, request, queryset):
        updated_count = queryset.update(is_available=False)
        self.message_user(
            request, 
            f"Successfully marked {updated_count} items as unavailable."
        )

    @admin.action(description="Mark selected items as Available")
    def make_available(self, request, queryset):
        updated_count = queryset.update(is_available=True)
        self.message_user(
            request, 
            f"Successfully marked {updated_count} items as available."
        )

# 2. Create the ModelAdmin class
class RestaurantAdmin(admin.ModelAdmin):
    # 3. Define fields visible in the list view table
    list_display = ('name', 'address', 'has_delivery')

    # 4. Enable a search bar for specific fields
    search_fields = ('name', 'address')

    # 5. Add a sidebar filter for boolean or categorical fields
    list_filter = ('has_delivery',)

@admin.register(UserReview)
class UserReviewAdmin(admin.ModelAdmin):
    # This determines what you see in the table list
    list_display = ('user', 'menu_item', 'rating', 'review_date')
    # This adds a sidebar to filter by rating or date
    list_filter = ('rating', 'review_date')
    # This allows you to search by username or review text
    search_fields = ('user__username', 'comment')    


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    # This displays these columns in the admin list view
    list_display = ('table_number', 'capacity', 'is_available')
    # This adds a filter sidebar on the right
    list_filter = ('is_available', 'capacity')
    # This allows you to search by table number
    search_fields = ('table_number',)

    
# 6. Register the model with its custom Admin class
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Ingredient)
admin.site.register(MenuCategory)
admin.site.register(Cuisine)
