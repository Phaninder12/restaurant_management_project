from django.contrib import admin
from .models import Order, OrderItem, Coupon, OrderStatus


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('item', 'quantity', 'price_at_time')
    readonly_fields = ('subtotal',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'final_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'customer__email')
    date_hierarchy = 'created_at'

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
        """
        Show OrderItem inline only when editing an existing order
        (obj is not None), hide it completely when adding a new one.
        """
        if obj is None:  # ← adding new order
            return []
        return [OrderItemInline]


admin.site.register(Coupon)
admin.site.register(OrderStatus)