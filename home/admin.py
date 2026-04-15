from django.contrib import admin # type: ignore
from .models import Restaurant,MenuItem, MenuCategory, Cuisine

# 2. Create the ModelAdmin class
class RestaurantAdmin(admin.ModelAdmin):
    # 3. Define fields visible in the list view table
    list_display = ('name', 'address', 'has_delivery')

    # 4. Enable a search bar for specific fields
    search_fields = ('name', 'address')

    # 5. Add a sidebar filter for boolean or categorical fields
    list_filter = ('has_delivery',)

# 6. Register the model with its custom Admin class
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(MenuItem)
admin.site.register(MenuCategory)
admin.site.register(Cuisine)