"""User management views for Manager to create/edit staff."""

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.urls import reverse

from management.forms import StaffUserForm
from management.permissions import manager_required


@manager_required
def staff_list(request):
    q = (request.GET.get('q') or '').strip()
    users = User.objects.filter(is_staff=True).order_by('username')
    if q:
        users = users.filter(username__icontains=q) | users.filter(first_name__icontains=q) | users.filter(last_name__icontains=q)
    return render(request, 'users/staff_list.html', {'users': users, 'q': q})


@manager_required
def staff_create(request):
    if request.method == 'POST':
        form = StaffUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.save()
            # assign to Staff group by default
            staff_group, _ = Group.objects.get_or_create(name='Staff')
            user.groups.add(staff_group)
            messages.success(request, 'Tạo tài khoản nhân viên thành công.')
            return redirect('staff_list')
    else:
        form = StaffUserForm()
    return render(request, 'users/staff_form.html', {'form': form, 'user_obj': None})


@manager_required
def staff_edit(request, user_id):
    user_obj = get_object_or_404(User, id=user_id, is_staff=True)
    if request.method == 'POST':
        form = StaffUserForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật nhân viên thành công.')
            return redirect('staff_list')
    else:
        form = StaffUserForm(instance=user_obj)
    return render(request, 'users/staff_form.html', {'form': form, 'user_obj': user_obj})


@manager_required
def staff_toggle_group(request, user_id, group_name):
    """Toggle membership in a group (Manager/Staff)."""
    user_obj = get_object_or_404(User, id=user_id)
    group = Group.objects.filter(name=group_name).first()
    if not group:
        messages.error(request, 'Nhóm không tồn tại.')
        return redirect('staff_list')
    if user_obj.groups.filter(name=group.name).exists():
        user_obj.groups.remove(group)
        messages.success(request, f'Đã gỡ {group.name} khỏi {user_obj.username}.')
    else:
        user_obj.groups.add(group)
        messages.success(request, f'Đã thêm {group.name} cho {user_obj.username}.')
    return redirect('staff_list')
