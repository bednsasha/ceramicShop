from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('image_preview', 'product', 'size', 'quantity',
              'price', 'get_total_price')
    readonly_fields = ('image_preview', 'get_total_price')
    can_delete = False

    def image_preview(self, obj):
        if obj.product.main_image:
            return mark_safe(f'<img src="{obj.product.main_image.url}" style="max-height: 80px; max-width: 80px; object-fit: cover; border-radius: 8px;" />')
        return mark_safe('<span style="color: #8B7D6B;">Нет изображения</span>')
    image_preview.short_description = 'Изображение'

    def get_total_price(self, obj):
        try:
            return f"{obj.get_total_price()} ₽"
        except (TypeError, AttributeError):
            return mark_safe('<span style="color: #E07A5F;">Ошибка</span>')
    get_total_price.short_description = 'Сумма'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'total_price',
                    'status', 'created_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('email', 'first_name', 'last_name', 'id')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'yookassa_payment_id')
    inlines = [OrderItemInline]

    fieldsets = (
        ('Информация о покупателе', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Адрес доставки', {
            'fields': ('company', 'address1', 'address2', 'city',
                       'province', 'postal_code', 'country')
        }),
        ('Информация о заказе', {
            'fields': ('total_price', 'status')
        }),
        ('Платёжная информация', {
            'fields': ('yookassa_payment_id',),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + (
                'user', 'first_name', 'last_name', 'email', 'phone',
                'company', 'address1', 'address2', 'city',
                'province', 'postal_code', 'country', 'total_price'
            )
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == 'completed':
            return False
        return super().has_delete_permission(request, obj)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'size', 'quantity', 'price', 'get_total_price')
    list_filter = ('order__status',)
    search_fields = ('order__email', 'product__name')
    readonly_fields = ('product', 'size', 'quantity', 'price', 'get_total_price')
    can_delete = False

    def get_total_price(self, obj):
        return f"{obj.get_total_price()} ₽"
    get_total_price.short_description = 'Сумма'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False