from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q, Count, F
from management.permissions import manager_required, manager_or_staff_required
from management.services.inventory_service import get_all_variants_stock, get_low_stock_variants
from management.models import ProductVariant

@manager_or_staff_required
def inventory_list(request):
    """
    View for listing all inventory items with search and filter capabilities.
    Staff users cannot see import_price.

    Decorators:
        @manager_or_staff_required: Both staff and manager can access.

    Query Parameters:
        q: Search by product name, SKU, or code
        color: Filter by color
        size: Filter by size
        brand: Filter by brand
        page: Page number for pagination

    Context:
        page_obj: Paginated ProductVariant objects
        search_query: Current search query
        colors, sizes, brands: Options for filter dropdowns
        is_manager: Boolean for template role-checking
        low_stock_count: Number of variants below min_quantity
        out_of_stock_count: Number of variants with 0 stock
    """
    # Get all active variants from service
    # Note: Service returns a list, but for filtering/search efficiency
    # we might prefer a QuerySet if the list is huge.
    # However, following the plan to use the service:
    variants = ProductVariant.objects.filter(is_active=True).select_related('product').order_by('product__name', 'color', 'size')

    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        variants = variants.filter(
            Q(product__name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(product__code__icontains=search_query)
        )

    # Filters
    color_filter = request.GET.get('color', '')
    if color_filter:
        variants = variants.filter(color=color_filter)

    size_filter = request.GET.get('size', '')
    if size_filter:
        variants = variants.filter(size=size_filter)

    brand_filter = request.GET.get('brand', '')
    if brand_filter:
        variants = variants.filter(product__brand=brand_filter)

    # Calculate counts before pagination
    low_stock_count = variants.filter(stock_quantity__lt=F('min_quantity')).count()
    out_of_stock_count = variants.filter(stock_quantity=0).count()

    # Pagination
    paginator = Paginator(variants, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter options for dropdowns
    colors = ProductVariant.objects.filter(is_active=True).values_list('color', flat=True).distinct().order_by('color')
    sizes = ProductVariant.objects.filter(is_active=True).values_list('size', flat=True).distinct().order_by('size')
    brands = ProductVariant.objects.filter(is_active=True).values_list('product__brand', flat=True).distinct().order_by('product__brand')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'colors': colors,
        'sizes': sizes,
        'brands': brands,
        'selected_color': color_filter,
        'selected_size': size_filter,
        'selected_brand': brand_filter,
        'is_manager': request.user.groups.filter(name='Manager').exists() or request.user.is_superuser,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
    }

    return render(request, 'inventory/inventory_list.html', context)

@manager_required
def inventory_low_stock(request):
    """
    View for specifically listing low stock items.
    Only accessible by Managers.

    Decorators:
        @manager_required: Only managers can access this view.

    Context:
        page_obj: Low stock ProductVariant objects (from service)
        title: Vietnamese title for the page
        is_manager: Always True for this view
        low_stock_count: Number of low stock items
        out_of_stock_count: Number of out of stock items
    """
    # Use service to get low stock items
    low_stock_variants = get_low_stock_variants()

    # Calculate counts
    low_stock_count = len(low_stock_variants)
    out_of_stock_count = sum(1 for v in low_stock_variants if v.stock_quantity == 0)

    context = {
        'page_obj': low_stock_variants,
        'title': 'Cảnh báo tồn kho thấp',
        'is_manager': True,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
    }
    return render(request, 'inventory/inventory_list.html', context)
