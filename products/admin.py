from django.contrib import admin
from .models import Category, SizeAttribute, ProductSize, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class SizeAttributeInline(admin.TabularInline):

    model = SizeAttribute
    extra = 1
    fields = ['attribute_type']


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1
    # Отображение размеров для конкретной категории

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "size":
            product_id = request.resolver_match.kwargs.get('object_id')
            if product_id:
                product = Product.objects.get(id=product_id)
                kwargs["queryset"] = SizeAttribute.objects.filter(
                    category=product.category
                )
            else:
                kwargs["queryset"] = SizeAttribute.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "color",
                    "price", "glaze_type", 'get_sizes_info']
    list_filter = ["category", "color", "glaze_type"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductSizeInline]

    def get_sizes_info(self, obj):
        sizes = obj.product_sizes.all()
        if sizes:
            return ", ".join([f"{s.size.get_attribute_type_display()}: {s.value}" for s in sizes[:3]])
        return "Нет размеров"
    get_sizes_info.short_description = "Размеры"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SizeAttributeInline]


class SizeAdmin(admin.ModelAdmin):
    list_display = ['category', 'get_attribute_type_display']
    list_filter = ['category', 'attribute_type']
    search_fields = ['category__name']


admin.site.register(Product, ProductAdmin)
admin.site.register(SizeAttribute, SizeAdmin)
