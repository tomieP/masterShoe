from django.contrib import admin
from .models import Supplier, Product, ProductVariant

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'address']
    search_fields = ['name', 'phone']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'brand', 'type', 'is_active']
    list_filter = ['is_active', 'brand', 'type']
    search_fields = ['code', 'name', 'brand']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'color', 'size', 'selling_price', 'stock_quantity', 'min_quantity', 'is_active']
    list_filter = ['is_active', 'color', 'size']
    search_fields = ['product__name', 'product__code', 'sku']
    autocomplete_fields = ['product']
