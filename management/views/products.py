from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.http import Http404

from management.models import Product, ProductVariant
from management.forms import ProductForm, ProductVariantForm
from management.permissions import manager_required


@manager_required
def product_list(request):
    """
    Danh sách sản phẩm (phân trang 20, filter, search)
    GET: Hiển thị danh sách
    """
    query = request.GET.get('search', '')
    filter_type = request.GET.get('type', '')

    products = Product.objects.all().prefetch_related('variants').order_by('-updated_at')

    # Search by name, brand, code
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query) |
            Q(brand__icontains=query)
        )

    # Filter by type
    if filter_type:
        products = products.filter(type=filter_type)

    # Get all types for filter dropdown
    all_types = Product.objects.values_list('type', flat=True).distinct().order_by('type')

    # Pagination (20 per page)
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'search_query': query,
        'filter_type': filter_type,
        'all_types': all_types,
    }
    return render(request, 'products/product_list.html', context)


@manager_required
@require_http_methods(["GET", "POST"])
def product_create(request):
    """
    Tạo sản phẩm + biến thể
    GET: Hiển thị form
    POST: Lưu sản phẩm + biến thể
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Sản phẩm "{product.name}" đã được tạo thành công.')
            return redirect('product_detail', pk=product.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm()

    context = {
        'form': form,
        'title': 'Tạo sản phẩm mới',
        'button_text': 'Tạo sản phẩm'
    }
    return render(request, 'products/product_form.html', context)


@manager_required
def product_detail(request, pk):
    """
    Xem chi tiết sản phẩm & các biến thể
    GET: Hiển thị chi tiết
    """
    product = get_object_or_404(Product, pk=pk)
    variants = product.variants.all()

    context = {
        'product': product,
        'variants': variants,
    }
    return render(request, 'products/product_detail.html', context)


@manager_required
@require_http_methods(["GET", "POST"])
def product_edit(request, pk):
    """
    Sửa sản phẩm
    GET: Hiển thị form
    POST: Lưu thay đổi
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Sản phẩm "{product.name}" đã được cập nhật.')
            return redirect('product_detail', pk=product.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'title': f'Chỉnh sửa: {product.name}',
        'button_text': 'Cập nhật'
    }
    return render(request, 'products/product_form.html', context)


@manager_required
@require_http_methods(["POST"])
def product_delete(request, pk):
    """
    Soft delete sản phẩm (đánh dấu is_active = False)
    POST: Thực hiện xóa
    """
    product = get_object_or_404(Product, pk=pk)
    product_name = product.name
    product.is_active = False
    product.save()
    messages.success(request, f'Sản phẩm "{product_name}" đã được xóa.')
    return redirect('product_list')


@manager_required
@require_http_methods(["GET", "POST"])
def variant_create(request, product_id):
    """
    Thêm biến thể vào sản phẩm
    GET: Hiển thị form
    POST: Lưu biến thể
    """
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        form = ProductVariantForm(request.POST)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.save()
            messages.success(request, f'Biến thể "{variant}" đã được thêm.')
            return redirect('product_detail', pk=product.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductVariantForm()

    context = {
        'form': form,
        'product': product,
        'title': f'Thêm biến thể: {product.name}',
        'button_text': 'Thêm biến thể'
    }
    return render(request, 'products/variant_form.html', context)


@manager_required
@require_http_methods(["GET", "POST"])
def variant_edit(request, pk):
    """
    Sửa biến thể
    GET: Hiển thị form
    POST: Lưu thay đổi
    """
    variant = get_object_or_404(ProductVariant, pk=pk)

    if request.method == 'POST':
        form = ProductVariantForm(request.POST, instance=variant)
        if form.is_valid():
            variant = form.save()
            messages.success(request, f'Biến thể "{variant}" đã được cập nhật.')
            return redirect('product_detail', pk=variant.product.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductVariantForm(instance=variant)

    context = {
        'form': form,
        'variant': variant,
        'product': variant.product,
        'title': f'Chỉnh sửa biến thể: {variant}',
        'button_text': 'Cập nhật'
    }
    return render(request, 'products/variant_form.html', context)


@manager_required
@require_http_methods(["POST"])
def variant_delete(request, pk):
    """
    Xóa biến thể
    POST: Thực hiện xóa
    """
    variant = get_object_or_404(ProductVariant, pk=pk)
    product_id = variant.product.pk
    variant_name = str(variant)
    variant.delete()
    messages.success(request, f'Biến thể "{variant_name}" đã được xóa.')
    return redirect('product_detail', pk=product_id)
