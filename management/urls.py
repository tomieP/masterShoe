"""
URL configuration for management app.
"""
from django.urls import path
from management.views import auth, dashboard, products

urlpatterns = [

    #Auth
    path('login/', auth.login_view, name='login'),
    path('logout/', auth.logout_view, name='logout'),

    #Dashboard
    path('', dashboard.dashboard_view, name='dashboard'),

    #Products
    path('products/', products.product_list, name='product_list'),
    path('products/create/', products.product_create, name='product_create'),
    path('products/<int:pk>/', products.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', products.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', products.product_delete, name='product_delete'),
    path('products/<int:product_id>/variants/create/', products.variant_create, name='variant_create'),
    path('variants/<int:pk>/edit/', products.variant_edit, name='variant_edit'),
    path('variants/<int:pk>/delete/', products.variant_delete, name='variant_delete'),
]
