from django import forms
from django.contrib.auth.models import User, Group

from management.models import Product, ProductVariant, PurchaseOrder, PurchaseOrderItem, Supplier


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['code', 'name', 'brand', 'image', 'description', 'type', 'subtype', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập mã sản phẩm'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên sản phẩm'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập thương hiệu (tùy chọn)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Nhập mô tả sản phẩm'
            }),
            'type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập loại giày'
            }),
            'subtype': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập phân loại phụ (tùy chọn)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'code': 'Mã sản phẩm',
            'name': 'Tên sản phẩm',
            'brand': 'Thương hiệu',
            'image': 'Hình ảnh',
            'description': 'Mô tả',
            'type': 'Loại giày',
            'subtype': 'Phân loại phụ',
            'is_active': 'Đang hoạt động'
        }


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['color', 'size', 'import_price', 'selling_price', 'sku', 'stock_quantity', 'min_quantity', 'is_active']
        widgets = {
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập màu sắc'
            }),
            'size': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập kích thước'
            }),
            'import_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Nhập giá nhập'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Nhập giá bán'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập SKU (mã biến thể)'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Nhập số lượng tồn kho'
            }),
            'min_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Nhập tồn tối thiểu'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'color': 'Màu sắc',
            'size': 'Kích thước',
            'import_price': 'Giá nhập',
            'selling_price': 'Giá bán',
            'sku': 'SKU',
            'stock_quantity': 'Số lượng tồn',
            'min_quantity': 'Tồn tối thiểu',
            'is_active': 'Cho phép bán'
        }


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'notes', 'status']
        widgets = {
            'supplier': forms.Select(attrs={
                'class': 'form-select',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Nhập ghi chú phiếu nhập...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            })
        }
        labels = {
            'supplier': 'Nhà cung cấp',
            'notes': 'Ghi chú',
            'status': 'Trạng thái'
        }


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['variant', 'quantity', 'actual_import_price']
        widgets = {
            'variant': forms.Select(attrs={
                'class': 'form-select select-variant',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
            }),
            'actual_import_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            })
        }
        labels = {
            'variant': 'Sản phẩm',
            'quantity': 'SL',
            'actual_import_price': 'Giá nhập'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Chỉ hiển thị các biến thể đang hoạt động
        self.fields['variant'].queryset = ProductVariant.objects.filter(is_active=True).select_related('product')


from django.forms import inlineformset_factory
PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=1,
    can_delete=True
)


class SalesOrderForm(forms.Form):
    """Form for sales order checkout"""
    customer_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tên khách hàng (tùy chọn)'
        })
    )
    customer_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Số điện thoại (tùy chọn)'
        })
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('cash', 'Tiền mặt'),
            ('transfer', 'Chuyển khoản')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='cash'
    )
    payment_status = forms.ChoiceField(
        choices=[
            ('finished', 'Đã thanh toán'),
            ('owe', 'Còn nợ')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='finished'
    )


class SupplierForm(forms.ModelForm):
    """Form for creating and editing suppliers."""
    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên nhà cung cấp'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập số điện thoại'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Nhập địa chỉ'
            }),
        }
        labels = {
            'name': 'Tên nhà cung cấp',
            'phone': 'Số điện thoại',
            'address': 'Địa chỉ',
        }


class StaffUserForm(forms.ModelForm):
    """Form for creating/editing staff users by manager."""
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get('password')
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
        return user
