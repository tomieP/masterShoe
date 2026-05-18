"""
Purchase Order Views - Management of purchase orders (phiếu nhập hàng).

Views:
- purchase_list: Danh sách phiếu nhập (phân trang, filter, search)
- purchase_create: Tạo phiếu nhập mới
- purchase_detail: Xem chi tiết phiếu nhập
- purchase_edit: Sửa phiếu nhập (chỉ khi status = waiting)
- purchase_delete: Hủy phiếu nhập (soft delete / cancel)

Decorator: @manager_required - Chỉ Manager được phép truy cập
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden

from management.permissions import manager_required
from management.models import PurchaseOrder, PurchaseOrderItem, Supplier
from management.forms import PurchaseOrderForm, PurchaseOrderItemFormSet
from management.services.purchase import (
    create_purchase_order as service_create_purchase_order,
    get_purchase_order_detail as service_get_purchase_order_detail,
    update_purchase_order_status as service_update_purchase_order_status,
    PurchaseOrderError
)


@login_required
@manager_required
def purchase_list(request):
    """
    Danh sách phiếu nhập hàng với phân trang, filter và search.

    GET parameters:
    - q: Search by order code, supplier name
    - status: Filter by status (waiting, finished, canceled)
    - supplier: Filter by supplier
    - page: Page number for pagination
    """
    # Lấy tất cả orders, sắp xếp theo ngày tạo mới nhất
    orders = PurchaseOrder.objects.select_related('supplier', 'created_by').order_by('-created_at')

    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        orders = orders.filter(
            Q(code__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Filter by supplier
    supplier_filter = request.GET.get('supplier', '')
    if supplier_filter:
        orders = orders.filter(supplier_id=supplier_filter)

    # Pagination (20 per page)
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Lấy danh sách suppliers cho filter dropdown
    suppliers = Supplier.objects.all().order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'supplier_filter': supplier_filter,
        'suppliers': suppliers,
    }

    return render(request, 'purchase/purchase_list.html', context)


@login_required
@manager_required
def purchase_create(request):
    """
    Tạo phiếu nhập hàng mới.

    GET: Hiển thị form trống
    POST: Xử lý tạo order với items từ formset
    """
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            # Kiểm tra có ít nhất 1 item
            if not formset.cleaned_data or all(item.get('DELETE', False) for item in formset.cleaned_data if item):
                messages.error(request, 'Phiếu nhập phải có ít nhất một sản phẩm.')
                return render(request, 'purchase/purchase_form.html', {
                    'form': form,
                    'formset': formset,
                    'is_edit': False,
                })

            try:
                # Chuẩn bị items_data cho service
                items_data = []
                for item in formset.cleaned_data:
                    if item.get('DELETE', False):
                        continue
                    if not item.get('variant', None) or not item.get('quantity', None):
                        continue

                    items_data.append({
                        'variant': item['variant'].id,
                        'quantity': item['quantity'],
                        'price': item.get('actual_import_price', 0),
                    })

                if not items_data:
                    messages.error(request, 'Phiếu nhập phải có ít nhất một sản phẩm hợp lệ.')
                    return render(request, 'purchase/purchase_form.html', {
                        'form': form,
                        'formset': formset,
                        'is_edit': False,
                    })

                # Gọi service để tạo order
                order = service_create_purchase_order(
                    supplier=form.cleaned_data['supplier'],
                    items_data=items_data,
                    user=request.user,
                    notes=form.cleaned_data.get('notes', ''),
                    status=form.cleaned_data.get('status', 'waiting')
                )

                messages.success(request, f'Đã tạo phiếu nhập {order.code} thành công!')
                return redirect('purchase_detail', order_id=order.id)

            except PurchaseOrderError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Lỗi: {str(e)}')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin phiếu nhập.')
    else:
        form = PurchaseOrderForm()
        formset = PurchaseOrderItemFormSet()

    context = {
        'form': form,
        'formset': formset,
        'is_edit': False,
    }

    return render(request, 'purchase/purchase_form.html', context)


@login_required
@manager_required
def purchase_detail(request, order_id):
    """
    Xem chi tiết phiếu nhập hàng.
    """
    try:
        order = service_get_purchase_order_detail(order_id)
    except PurchaseOrderError:
        messages.error(request, 'Phiếu nhập không tồn tại.')
        return redirect('purchase_list')

    context = {
        'order': order,
    }

    return render(request, 'purchase/purchase_detail.html', context)


@login_required
@manager_required
def purchase_edit(request, order_id):
    """
    Sửa phiếu nhập hàng. Chỉ cho phép khi status = 'waiting'.

    GET: Hiển thị form với dữ liệu hiện có
    POST: Cập nhật order và items
    """
    order = get_object_or_404(PurchaseOrder, id=order_id)

    # Chỉ cho phép sửa khi status = waiting
    if order.status != 'waiting':
        messages.warning(request, f'Không thể sửa phiếu nhập đang ở trạng thái "{order.get_status_display()}".')
        return redirect('purchase_detail', order_id=order.id)

    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=order)
        formset = PurchaseOrderItemFormSet(request.POST, instance=order)

        if form.is_valid() and formset.is_valid():
            # Kiểm tra có ít nhất 1 item
            valid_items = [item for item in formset.cleaned_data if not item.get('DELETE', False) and item.get('variant')]
            if not valid_items:
                messages.error(request, 'Phiếu nhập phải có ít nhất một sản phẩm.')
                return render(request, 'purchase/purchase_form.html', {
                    'form': form,
                    'formset': formset,
                    'is_edit': True,
                    'order': order,
                })

            try:
                # Xóa các items cũ
                order.items.all().delete()

                # Chuẩn bị items_data cho service
                items_data = []
                for item in valid_items:
                    items_data.append({
                        'variant': item['variant'].id,
                        'quantity': item['quantity'],
                        'price': item.get('actual_import_price', 0),
                    })

                # Cập nhật thông tin order (tạo mới items)
                order.supplier = form.cleaned_data['supplier']
                order.notes = form.cleaned_data.get('notes', '')
                order.total_amount = sum(item['quantity'] * item['price'] for item in items_data)
                order.save()

                # Tạo lại items
                for item_data in items_data:
                    PurchaseOrderItem.objects.create(
                        purchase_order=order,
                        variant_id=item_data['variant'],
                        quantity=item_data['quantity'],
                        actual_import_price=item_data['price']
                    )

                messages.success(request, f'Đã cập nhật phiếu nhập {order.code} thành công!')
                return redirect('purchase_detail', order_id=order.id)

            except Exception as e:
                messages.error(request, f'Lỗi: {str(e)}')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin phiếu nhập.')
    else:
        form = PurchaseOrderForm(instance=order)
        formset = PurchaseOrderItemFormSet(instance=order)

    context = {
        'form': form,
        'formset': formset,
        'is_edit': True,
        'order': order,
    }

    return render(request, 'purchase/purchase_form.html', context)


@login_required
@manager_required
def purchase_delete(request, order_id):
    """
    Hủy phiếu nhập hàng. Chỉ cho phép khi status = 'waiting' hoặc 'finished'.

    GET: Hiển thị trang xác nhận
    POST: Thực hiện hủy (đổi status thành canceled)
    """
    order = get_object_or_404(PurchaseOrder, id=order_id)

    if request.method == 'POST':
        try:
            # Chỉ hủy được các đơn ở trạng thái waiting hoặc finished
            if order.status == 'canceled':
                messages.warning(request, 'Phiếu nhập này đã bị hủy trước đó.')
            else:
                service_update_purchase_order_status(order.id, 'canceled')
                messages.success(request, f'Đã hủy phiếu nhập {order.code} thành công!')

            return redirect('purchase_list')

        except PurchaseOrderError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')

    context = {
        'order': order,
    }

    return render(request, 'purchase/purchase_confirm_delete.html', context)


@login_required
@manager_required
def purchase_update_status(request, order_id):
    """
    Cập nhật trạng thái phiếu nhập (hoàn thành/hủy).

    POST only:
    - status: new status (finished hoặc canceled)
    """
    if request.method == 'POST':
        order = get_object_or_404(PurchaseOrder, id=order_id)
        new_status = request.POST.get('status', '')

        if new_status not in ['finished', 'canceled']:
            messages.error(request, 'Trạng thái không hợp lệ.')
            return redirect('purchase_detail', order_id=order.id)

        try:
            service_update_purchase_order_status(order.id, new_status)
            status_display = dict(PurchaseOrder.STATUS_CHOICES).get(new_status, new_status)
            messages.success(request, f'Đã cập nhật trạng thái phiếu nhập {order.code} thành "{status_display}"!')
        except PurchaseOrderError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')

    return redirect('purchase_detail', order_id=order_id)