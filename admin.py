from django.contrib import admin # type: ignore
from .models import Order, OrderItem, Coupon, OrderStatus

# 1. Inline for Order Items
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('menu_item', 'quantity', 'price') 
    readonly_fields = ('price',) 

# 2. The Custom Action Function
@admin.action(description="Mark selected orders as Processed")
def mark_orders_processed(modeladmin, request, queryset):
    """
    Action function to update selected orders to 'Processed'.
    """
    updated_count = queryset.update(status='Processed')
    modeladmin.message_user(
        request, 
        f"Successfully marked {updated_count} orders as Processed."
    )

# 3. The Main Order Admin Class
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Use the custom action here
    actions = [mark_orders_processed]

    # Display settings
    list_display = ('id', 'customer', 'final_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'created_at'

    # Layout settings
    fieldsets = (
        (None, {
            'fields': ('user', 'status', 'applied_coupon')
        }),
        ('Prices (auto-calculated)', {
            'fields': ('total_price', 'discount_amount', 'final_price'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('total_price', 'discount_amount', 'final_price', 'created_at', 'updated_at')

    def get_inlines(self, request, obj=None):
        """Show OrderItem inline only when editing an existing order."""
        if obj is None: 
            return []
        return [OrderItemInline]

# 4. Register remaining models
admin.site.register(Coupon)
admin.site.register(OrderStatus)