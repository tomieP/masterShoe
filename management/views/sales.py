"""
Sales (POS) Views - Point of Sale interface and order management.

Views:
- pos_index: Main POS interface (product search + shopping cart)
- search_products: HTMX endpoint for product search
- checkout: Process checkout and create sales order
- sales_list: List of sales orders (filtered by user if staff)
- sales_detail: Detail view of a sales order
- sales_print: Print-friendly invoice view

Decorator: @staff_required - Staff and Manager can access
"""

import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from management.permissions import staff_required
from management.models import ProductVariant, SalesOrder
from management.forms import SalesOrderForm
from management.services.sales import (
    create_sales_order,
    get_sales_order_detail,
    calculate_profit,
    InsufficientStockError,
    VariantNotFoundError
)


@login_required
@staff_required
def pos_index(request):
    """
    Main POS interface with product search and shopping cart.
    """
    # Fetch initial products to show (e.g., latest 50 active variants)
    initial_variants = ProductVariant.objects.filter(
        is_active=True,
        stock_quantity__gt=0
    ).select_related('product').order_by('-id')[:50]

    context = {
        'form': SalesOrderForm(),
        'initial_variants': initial_variants,
    }
    return render(request, 'sales/pos.html', context)


@login_required
@staff_required
@require_http_methods(["GET"])
def search_products(request):
    """
    HTMX endpoint to search for product variants.
    """
    query = request.GET.get('q', '').strip()

    # Search variants by product name, SKU, or product code
    # If no query, show recent products
    variants_query = ProductVariant.objects.filter(
        is_active=True,
        stock_quantity__gt=0
    ).select_related('product')

    if query and len(query) >= 1:
        variants_query = variants_query.filter(
            Q(product__name__icontains=query) |
            Q(product__code__icontains=query) |
            Q(sku__icontains=query) |
            Q(product__brand__icontains=query)
        )

    variants = variants_query.order_by('product__name', 'color', 'size')[:50]

    context = {
        'variants': variants,
        'query': query,
    }

    return render(request, 'partials/product_search.html', context)


@login_required
@staff_required
@require_http_methods(["POST"])
def checkout(request):
    """
    Process checkout: validate cart data and create a sales order.

    Expected POST data:
    - items: JSON array of {variant_id, quantity}
    - customer_name: Optional
    - customer_phone: Optional
    - payment_method: 'cash' or 'transfer'
    - payment_status: 'finished' or 'owe'

    On success: Redirect to sales_print
    On failure: Return JSON with error message
    """
    try:
        # Parse cart items from POST
        items_json = request.POST.get('items', '[]')
        items_data = json.loads(items_json)

        # Validate items
        if not items_data or not isinstance(items_data, list):
            if request.headers.get('HX-Request'):
                return JsonResponse({'error': 'Giỏ hàng trống'}, status=400)
            messages.error(request, 'Giỏ hàng trống')
            return redirect('pos_index')

        # Parse form data
        form = SalesOrderForm(request.POST)
        if not form.is_valid():
            if request.headers.get('HX-Request'):
                return JsonResponse({'error': 'Dữ liệu thanh toán không hợp lệ'}, status=400)
            messages.error(request, 'Dữ liệu thanh toán không hợp lệ')
            return redirect('pos_index')

        # Create sales order
        order = create_sales_order(
            items_data=items_data,
            user=request.user,
            customer_name=form.cleaned_data.get('customer_name', ''),
            customer_phone=form.cleaned_data.get('customer_phone', ''),
            payment_method=form.cleaned_data.get('payment_method', 'cash'),
            payment_status=form.cleaned_data.get('payment_status', 'finished')
        )

        messages.success(request, f'Hóa đơn {order.code} đã được tạo thành công!')
        return redirect('sales_print', order_id=order.id)

    except InsufficientStockError as e:
        error_msg = f'Sản phẩm ID {e.variant_id} không đủ hàng. Hiện có: {e.available}, yêu cầu: {e.requested}'
        if request.headers.get('HX-Request'):
            return JsonResponse({'error': error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect('pos_index')

    except VariantNotFoundError as e:
        error_msg = f'Sản phẩm ID {e.variant_id} không tồn tại hoặc đã ngừng bán'
        if request.headers.get('HX-Request'):
            return JsonResponse({'error': error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect('pos_index')

    except (ValueError, json.JSONDecodeError) as e:
        error_msg = f'Dữ liệu không hợp lệ: {str(e)}'
        if request.headers.get('HX-Request'):
            return JsonResponse({'error': error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect('pos_index')


@login_required
@staff_required
def sales_list(request):
    """
    List of sales orders.

    GET parameters:
    - q: Search by order code or customer name
    - page: Page number for pagination

    Filtering:
    - Staff users see only their own orders
    - Manager users see all orders
    """
    # Check if user is manager
    is_manager = request.user.is_superuser or request.user.groups.filter(name='Manager').exists()

    # Filter orders based on role
    if is_manager:
        orders = SalesOrder.objects.all()
    else:
        orders = SalesOrder.objects.filter(created_by=request.user)

    # Sort by most recent first
    orders = orders.select_related('created_by').order_by('-sale_date')

    # Search by order code or customer name
    search_query = request.GET.get('q', '')
    if search_query:
        orders = orders.filter(
            Q(code__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(customer_phone__icontains=search_query)
        )

    # Pagination (20 per page)
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'is_manager': is_manager,
    }

    return render(request, 'sales/sales_list.html', context)


@login_required
@staff_required
def sales_detail(request, order_id):
    """
    Detail view of a sales order.

    Staff users can only view their own orders (unless superuser/manager).
    """
    order = get_sales_order_detail(order_id)

    # Check permission: staff can only see their own orders
    is_manager = request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    if not is_manager and order.created_by != request.user:
        messages.error(request, 'Bạn không có quyền xem hóa đơn này')
        return redirect('sales_list')

    context = {
        'order': order,
        'items': order.items.all(),
        'is_manager': is_manager,
    }

    return render(request, 'sales/sales_detail.html', context)


@login_required
@staff_required
def sales_print(request, order_id):
    """
    Print-friendly invoice view.

    Staff users can only print their own orders (unless superuser/manager).
    """
    order = get_sales_order_detail(order_id)

    # Check permission: staff can only print their own orders
    is_manager = request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
    if not is_manager and order.created_by != request.user:
        messages.error(request, 'Bạn không có quyền in hóa đơn này')
        return redirect('sales_list')

    context = {
        'order': order,
        'items': order.items.all(),
    }

    return render(request, 'sales/sales_print.html', context)
