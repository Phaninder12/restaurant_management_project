from django.contrib import admin
from .models import Order, OrderItem, Coupon, OrderStatus, PaymentMethod

# 1. Inline for Order Items
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # Updated to match fields in your OrderItem model
    fields = ('item', 'quantity', 'price_at_time') 
    readonly_fields = ('price_at_time',) 

# 2. The Custom Action Function
@admin.action(description="Mark selected orders as Processed")
def mark_orders_processed(modeladmin, request, queryset):
    # Updated 'Processed' to 'processing' to match your STATUS_CHOICES
    updated_count = queryset.update(status='processing')
    modeladmin.message_user(
        request, 
        f"Successfully marked {updated_count} orders as Processing."
    )

# 3. The Main Order Admin Class
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    actions = [mark_orders_processed]

    # Display settings
    list_display = ('order_id', 'customer', 'final_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    # Updated to 'customer__username' to match your model
    search_fields = ('customer__username', 'customer__email', 'order_id')
    date_hierarchy = 'created_at'

    # Layout settings
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

    readonly_fields = ('total_price', 'discount_amount', 'final_price', 'created_at', 'updated_at')

    def get_inlines(self, request, obj=None):
        """Show OrderItem inline only when editing an existing order."""
        if obj is None: 
            return []
        return [OrderItemInline]

    # --- SHOW TOTAL REVENUE ON ADMIN PAGE ---
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Get the revenue from the class method we created!
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