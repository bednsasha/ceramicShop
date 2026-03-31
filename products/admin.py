from django.contrib import admin
from .models import Category, SizeAttribute, ProductSize, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "color", "price", "glaze_type"]
    list_filter = ["category", "color", "glaze_type"]
    search_fields = ["name", "color", "description"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductSizeInline]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


class SizeAdmin(admin.ModelAdmin):
    list_display = ["attribute_type"]


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SizeAttribute, SizeAdmin)
