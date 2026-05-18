"""Supplier management views."""

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages

from management.forms import SupplierForm
from management.models import Supplier
from management.permissions import manager_required


@manager_required
def supplier_list(request):
    q = (request.GET.get('q') or '').strip()

    suppliers = Supplier.objects.all().order_by('name')
    if q:
        suppliers = suppliers.filter(
            Q(name__icontains=q) |
            Q(phone__icontains=q) |
            Q(address__icontains=q)
        )

    paginator = Paginator(suppliers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'suppliers/supplier_list.html', {
        'q': q,
        'page_obj': page_obj,
    })


@manager_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, 'Tạo nhà cung cấp thành công.')
            return redirect('supplier_list')
    else:
        form = SupplierForm()

    return render(request, 'suppliers/supplier_form.html', {
        'form': form,
        'supplier': None,
    })


@manager_required
def supplier_edit(request, supplier_id: int):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật nhà cung cấp thành công.')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'suppliers/supplier_form.html', {
        'form': form,
        'supplier': supplier,
    })


@manager_required
def supplier_delete(request, supplier_id: int):
    if request.method != 'POST':
        return redirect('supplier_list')

    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.delete()
    messages.success(request, 'Đã xóa nhà cung cấp.')
    return redirect('supplier_list')
