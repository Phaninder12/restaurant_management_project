from django.contrib import admin # type: ignore
from .models import Restaurant

# 2. Create the ModelAdmin class
class RestaurantAdmin(admin.ModelAdmin):
    # 3. Define fields visible in the list view table
    list_display = ('name', 'address', 'phone_number', 'email', 'is_active')
    
    # 4. Enable a search bar for specific fields
    # Use a tuple (note the trailing comma if it were a single item)
    search_fields = ('name', 'address')
    
    # 5. Add a sidebar filter for boolean or categorical fields
    list_filter = ('is_active',)

# 6. Register the model with its custom Admin class
admin.site.register(Restaurant, RestaurantAdmin)             