from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Supplier, Product, ProductVariant,
    PurchaseOrder, PurchaseOrderItem,
    SalesOrder, SalesOrderItem,
)


# ─── Supplier ────────────────────────────────────────────────────────────────

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'address']
    search_fields = ['name', 'phone']
    ordering = ['name']


# ─── Product ─────────────────────────────────────────────────────────────────

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'brand', 'type', 'subtype', 'is_active', 'created_at']
    list_filter = ['is_active', 'brand', 'type']
    search_fields = ['code', 'name', 'brand']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['code']


# ─── ProductVariant ──────────────────────────────────────────────────────────

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = [
        'sku', 'product', 'color', 'size',
        'import_price', 'selling_price', 'stock_quantity', 'min_quantity', 'is_active',
    ]
    list_filter = ['is_active', 'color', 'size']
    search_fields = ['product__name', 'product__code', 'sku']
    autocomplete_fields = ['product']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['product__code', 'color', 'size']


# ─── PurchaseOrder ───────────────────────────────────────────────────────────

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0
    readonly_fields = ['subtotal']
    fields = ['variant', 'quantity', 'actual_import_price', 'subtotal']

    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = 'Thành tiền'


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['code', 'supplier', 'order_date', 'status', 'total_amount', 'created_by']
    list_filter = ['status', 'supplier', 'order_date']
    search_fields = ['code', 'supplier__name', 'created_by__username']
    readonly_fields = ['code', 'created_at', 'updated_at', 'created_by']
    ordering = ['-order_date']
    inlines = [PurchaseOrderItemInline]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ─── SalesOrder ──────────────────────────────────────────────────────────────

class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 0
    readonly_fields = ['subtotal']
    fields = ['variant', 'quantity', 'selling_price_at_time', 'subtotal']

    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = 'Thành tiền'


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'customer_name', 'customer_phone',
        'sale_date', 'total_amount', 'payment_method', 'payment_status', 'created_by',
    ]
    list_filter = ['payment_method', 'payment_status', 'sale_date']
    search_fields = ['code', 'customer_name', 'customer_phone', 'created_by__username']
    readonly_fields = ['code', 'created_at', 'updated_at', 'created_by']
    ordering = ['-sale_date']
    inlines = [SalesOrderItemInline]


# ─── User Management ─────────────────────────────────────────────────────────

class StaffGroupFilter(admin.SimpleListFilter):
    """Filter users by role group."""
    title = 'Vai trò'
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        return [
            ('Manager', 'Manager'),
            ('Staff', 'Staff'),
            ('none', 'Chưa có nhóm'),
        ]

    def queryset(self, request, queryset):
        if self.value() in ('Manager', 'Staff'):
            return queryset.filter(groups__name=self.value())
        if self.value() == 'none':
            return queryset.filter(groups__isnull=True)
        return queryset


class CustomUserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'get_full_name', 'email',
        'get_role', 'is_active', 'last_login', 'date_joined',
    ]
    list_filter = ['is_active', StaffGroupFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['username']


    @admin.display(description='Họ tên')
    def get_full_name(self, obj):
        return obj.get_full_name() or '—'

    @admin.display(description='Vai trò')
    def get_role(self, obj):
        groups = list(obj.groups.values_list('name', flat=True))
        return ', '.join(groups) if groups else '—'


# Re-register User with custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
