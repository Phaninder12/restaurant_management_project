from django.contrib import admin
from .models import Order, OrderItem, Coupon, OrderStatus, PaymentMethod

# 1. Inline for Order Items
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    # Changed extra to 1 so you see one empty row immediately
    extra = 1 
    # Removed readonly_fields so you can manually enter the price_at_time
    fields = ('item', 'quantity', 'price_at_time') 

# 2. The Custom Action Function
@admin.action(description="Mark selected orders as Processed")
def mark_orders_processed(modeladmin, request, queryset):
    updated_count = queryset.update(status='processing')
    modeladmin.message_user(
        request, 
        f"Successfully marked {updated_count} orders as Processing."
    )

# 3. The Main Order Admin Class
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    actions = [mark_orders_processed]
    
    # We now show the inline ALL the time (both on Add and Edit)
    inlines = [OrderItemInline]

    # Display settings for the list view
    list_display = ('order_id', 'customer', 'final_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'customer__email', 'order_id')
    date_hierarchy = 'created_at'

    # Layout settings for the detail view
    fieldsets = (
        (None, {
            'fields': ('customer', 'status', 'applied_coupon')
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

    # These fields are calculated by our model methods, so we keep them read-only in the form
    readonly_fields = ('total_price', 'discount_amount', 'final_price', 'created_at', 'updated_at')

    # --- SHOW TOTAL REVENUE ON ADMIN PAGE ---
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Get the revenue from the class method in models.py
        extra_context['total_revenue'] = Order.calculate_total_revenue()
        return super().changelist_view(request, extra_context=extra_context)
    
@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'description')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)

# 4. Register remaining models
admin.site.register(Coupon)
admin.site.register(OrderStatus)
# Registering OrderItem separately as well so it shows in the sidebar
admin.site.register(OrderItem)
