from django import forms
from .models import Product, ProductVariant


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