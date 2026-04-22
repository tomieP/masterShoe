from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên nhà cung cấp")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Nhà cung cấp"
        verbose_name_plural = "Nhà cung cấp"

class Product(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã sản phẩm")
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    brand = models.CharField(max_length=100, blank=True, null=True, verbose_name="Thương hiệu")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Hình ảnh")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    type = models.CharField(max_length=100, verbose_name="Loại giày")
    subtype = models.CharField(max_length=100, blank=True, null=True, verbose_name="Phân loại phụ")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name="Sản phẩm")
    color = models.CharField(max_length=50, verbose_name="Màu sắc")
    size = models.CharField(max_length=20, verbose_name="Kích thước")
    import_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá nhập")
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá bán")
    sku = models.CharField(max_length=100, unique=True, verbose_name="SKU")
    stock_quantity = models.IntegerField(default=0, verbose_name="Số lượng tồn")
    min_quantity = models.IntegerField(default=5, verbose_name="Tồn tối thiểu")
    is_active = models.BooleanField(default=True, verbose_name="Cho phép bán")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.color} - {self.size}"

    class Meta:
        unique_together = ('product', 'color', 'size')
        verbose_name = "Biến thể sản phẩm"
        verbose_name_plural = "Biến thể sản phẩm"

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Đang chờ'),
        ('finished', 'Hoàn thành'),
        ('canceled', 'Đã hủy'),
    ]
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã đơn nhập")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="Nhà cung cấp")
    order_date = models.DateTimeField(default=timezone.now, verbose_name="Ngày nhập")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Tổng tiền")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Người tạo")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting', verbose_name="Trạng thái")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Đơn nhập hàng"
        verbose_name_plural = "Đơn nhập hàng"

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(verbose_name="Số lượng")
    actual_import_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá nhập thực tế")

    @property
    def subtotal(self):
        return self.quantity * self.actual_import_price

    class Meta:
        verbose_name = "Chi tiết đơn nhập"
        verbose_name_plural = "Chi tiết đơn nhập"

class SalesOrder(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Tiền mặt'),
        ('transfer', 'Chuyển khoản'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('finished', 'Đã thanh toán'),
        ('owe', 'Còn nợ'),
    ]
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã hóa đơn")
    customer_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên khách hàng")
    customer_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="SĐT khách hàng")
    sale_date = models.DateTimeField(default=timezone.now, verbose_name="Ngày bán")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Tổng cộng")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Người bán")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name="Phương thức thanh toán")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='finished', verbose_name="Trạng thái thanh toán")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Hóa đơn bán hàng"
        verbose_name_plural = "Hóa đơn bán hàng"

class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(verbose_name="Số lượng")
    selling_price_at_time = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá bán lúc đó")

    @property
    def subtotal(self):
        return self.quantity * self.selling_price_at_time

    class Meta:
        verbose_name = "Chi tiết hóa đơn"
        verbose_name_plural = "Chi tiết hóa đơn"
