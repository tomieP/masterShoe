"""
URL configuration for management app.
"""
from django.urls import path
from management.views import auth, dashboard, products, inventory, purchase, sales, suppliers, users, users

urlpatterns = [

    #Auth
    path('login/', auth.login_view, name='login'),
    path('logout/', auth.logout_view, name='logout'),

    #Dashboard & Reports
    path('', dashboard.dashboard, name='dashboard'),
    path('reports/period/', dashboard.reports_period, name='reports_period'),
    path('reports/top-products/', dashboard.reports_top_products, name='reports_top_products'),

    #Inventory
    path('inventory/', inventory.inventory_list, name='inventory_list'),
    path('inventory/low-stock/', inventory.inventory_low_stock, name='inventory_low_stock'),

    #Products
    path('products/', products.product_list, name='product_list'),
    path('products/create/', products.product_create, name='product_create'),
    path('products/<int:pk>/', products.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', products.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', products.product_delete, name='product_delete'),
    path('products/<int:product_id>/variants/create/', products.variant_create, name='variant_create'),
    path('variants/<int:pk>/edit/', products.variant_edit, name='variant_edit'),
    path('variants/<int:pk>/delete/', products.variant_delete, name='variant_delete'),

    #Purchase Orders
    path('purchase/', purchase.purchase_list, name='purchase_list'),
    path('purchase/create/', purchase.purchase_create, name='purchase_create'),
    path('purchase/<int:order_id>/', purchase.purchase_detail, name='purchase_detail'),
    path('purchase/<int:order_id>/edit/', purchase.purchase_edit, name='purchase_edit'),
    path('purchase/<int:order_id>/delete/', purchase.purchase_delete, name='purchase_delete'),
    path('purchase/<int:order_id>/update-status/', purchase.purchase_update_status, name='purchase_update_status'),

    #Suppliers
    path('suppliers/', suppliers.supplier_list, name='supplier_list'),
    path('suppliers/create/', suppliers.supplier_create, name='supplier_create'),
    path('suppliers/<int:supplier_id>/edit/', suppliers.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:supplier_id>/delete/', suppliers.supplier_delete, name='supplier_delete'),

    #Suppliers
    path('suppliers/', suppliers.supplier_list, name='supplier_list'),
    path('suppliers/create/', suppliers.supplier_create, name='supplier_create'),
    path('suppliers/<int:supplier_id>/edit/', suppliers.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:supplier_id>/delete/', suppliers.supplier_delete, name='supplier_delete'),

    #Users (Manager only)
    path('users/', users.staff_list, name='staff_list'),
    path('users/create/', users.staff_create, name='staff_create'),
    path('users/<int:user_id>/edit/', users.staff_edit, name='staff_edit'),
    path('users/<int:user_id>/toggle-group/<str:group_name>/', users.staff_toggle_group, name='staff_toggle_group'),

    #Sales (POS)
    path('sales/', sales.pos_index, name='pos_index'),
    path('sales/search/', sales.search_products, name='search_products'),
    path('sales/checkout/', sales.checkout, name='checkout'),
    path('sales/list/', sales.sales_list, name='sales_list'),
    path('sales/<int:order_id>/', sales.sales_detail, name='sales_detail'),
    path('sales/<int:order_id>/print/', sales.sales_print, name='sales_print'),
]
