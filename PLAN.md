# PLAN.md - Roadmap & Kế hoạch phát triển Web App Quản lý Tiệm Giày

## Tình trạng hiện tại (2026-04-22)
✅ **Hoàn thành:**
- Database schema được cập nhật với đầy đủ bảng sản phẩm, biến thể, nhà cung cấp, phiếu nhập, hóa đơn bán
- Django project setup hoàn chỉnh (MySQL, Media, Static files)
- Models được định nghĩa (Product, Variant, Supplier, Purchase/Sales Orders)
- Sample data đã được seeding (40 sản phẩm, 196 biến thể, 6 nhà cung cấp, 2 tài khoản mẫu)
- Cấu trúc thư mục được sắp xếp gọn gàng
- Custom command `seed_data` được tạo
- CLAUDE.md được cập nhật để hướng dẫn các phiên phát triển tiếp theo

⏳ **Chưa làm:**
- Views (tất cả)
- Forms
- Templates
- Permissions & Authentication
- Services (business logic)
- URLs routing
- Admin interface customization

---

## Phase 1: Authentication & Core Infrastructure (3-4 ngày)

### 1.1 Permissions & Decorators
**File**: `management/permissions.py`
- Tạo custom decorators: `@login_required`, `@staff_required`, `@manager_required`
- Sử dụng Django's built-in auth + Groups (Staff, Manager)
- Kiểm tra quyền trên views

**Công việc**:
- [ ] Viết decorators
- [ ] Test decorators với cả hai roles

### 1.2 Authentication Views
**File**: `management/views/auth.py`
- Login view (GET/POST)
- Logout view
- Optional: Register (chỉ manager tạo staff)

**Templates**: `templates/auth/`
- `login.html` - Form đăng nhập Bootstrap 5
- (Optional: registration page)

**Công việc**:
- [ ] Tạo login view
- [ ] Tạo logout view
- [ ] Tạo login template
- [ ] Đảm bảo CSRF protection
- [ ] Test login/logout

### 1.3 Base Template & Navigation
**File**: `templates/base.html`
- Responsive navbar (collapsible hamburger menu trên mobile)
- Sidebar điều hướng (thay đổi theo role)
- Footer
- HTMX + Alpine.js + Chart.js + Bootstrap 5 CDN

**Nội dung navbar**:
- Logo
- User info & Logout link

**Nội dung sidebar** (role-based):
- **Staff**: 
  - Dashboard (thống kê tổng hôm nay)
  - Bán hàng (POS)
  - Xem kho
  - Lịch sử hóa đơn
- **Manager**: 
  - Dashboard (thống kê chi tiết + báo cáo)
  - Quản lý sản phẩm
  - Nhập hàng
  - Bán hàng
  - Xem kho
  - Báo cáo
  - Quản lý nhà cung cấp
  - Quản lý tài khoản (admin link)

**Công việc**:
- [ ] Thiết kế base layout với Bootstrap 5
- [ ] Tạo navbar responsive
- [ ] Tạo sidebar với menu phân quyền
- [ ] Thêm logout button
- [ ] Test responsive trên mobile

### 1.4 URL Routing
**File**: `management/urls.py` & `shoe_store/urls.py`
- Kết nối các URLs cho auth, products, sales, purchase, inventory, reports, suppliers

**Công việc**:
- [ ] Tạo app-level URLs trong `management/urls.py`
- [ ] Include URLs từ `shoe_store/urls.py`
- [ ] Test URL routing

---

## Phase 2: Product Management (3-4 ngày)

### 2.1 Models & Admin
**File**: `management/admin.py`
- Customize Django Admin để hiển thị Products, Variants, Suppliers

**Công việc**:
- [ ] Thêm Product, ProductVariant vào admin
- [ ] Thêm Supplier vào admin
- [ ] Customize admin list_display, search_fields, filters

### 2.2 Product Views & Forms
**File**: `management/views/products.py` & `management/forms.py`

**Views cần thiết**:
- `product_list` (GET) - Danh sách sản phẩm (phân trang 20, filter, search)
- `product_create` (GET/POST) - Tạo sản phẩm + biến thể
- `product_detail` (GET) - Xem chi tiết sản phẩm & các biến thể
- `product_edit` (GET/POST) - Sửa sản phẩm
- `product_delete` (POST) - Soft delete
- `variant_create` (GET/POST) - Thêm biến thể vào sản phẩm
- `variant_edit` (GET/POST) - Sửa biến thể
- `variant_delete` (POST) - Xóa biến thể

**Forms**:
- `ProductForm` - name, brand, type, subtype, description, image, code (unique)
- `ProductVariantForm` - color, size, import_price, selling_price, sku (unique), min_quantity

**Decorator**: `@manager_required` (chỉ manager)

**Templates**: `templates/products/`
- `product_list.html` - Bảng danh sách (Bootstrap table, phân trang, search, filter)
- `product_form.html` - Form thêm/sửa sản phẩm
- `product_detail.html` - Xem chi tiết & danh sách biến thể
- `variant_form.html` - Form thêm/sửa biến thể

**Công việc**:
- [ ] Tạo ProductForm, ProductVariantForm
- [ ] Tạo product_list view (phân trang, search, filter)
- [ ] Tạo product_create view
- [ ] Tạo product_edit view
- [ ] Tạo product_delete view
- [ ] Tạo variant_create, variant_edit, variant_delete views
- [ ] Tạo templates
- [ ] Test CRUD operations

### 2.3 Excel Import (Manager)
**File**: `management/management/commands/import_excel.py`

**Cách dùng**: `python manage.py import_excel <file_path>`

**Tính năng**:
- Đọc file `.xlsx` (cột: Tên, Thương hiệu, Size, Màu, Giá nhập, Giá bán, Tồn)
- Tạo Product nếu chưa tồn tại (match tên + brand)
- Tạo ProductVariant cho mỗi size/màu
- Cảnh báo lỗi dòng (thiếu dữ liệu, giá không hợp lệ)

**Công việc**:
- [ ] Tạo import command sử dụng `openpyxl` hoặc `pandas`
- [ ] Xử lý lỗi dòng & log lỗi
- [ ] Test import với file mẫu 100+ sản phẩm

---

## Phase 3: Inventory & Stock Management (2-3 ngày)

### 3.1 Inventory Service
**File**: `management/services/inventory.py`

**Functions**:
- `check_stock(variant_id, qty)` - Kiểm tra tồn kho có đủ không
- `increase_stock(variant_id, qty, import_price=None)` - Tăng tồn (nhập hàng)
- `decrease_stock(variant_id, qty)` - Giảm tồn (bán hàng)
- `get_low_stock_variants(threshold=None)` - Danh sách biến thể dưới min_quantity
- `get_all_variants_stock()` - Tất cả biến thể với tồn kho

**Đặc điểm**:
- Sử dụng `transaction.atomic()` để đảm bảo consistency
- Raise exception nếu stock không đủ khi bán

**Công việc**:
- [ ] Tạo inventory service
- [ ] Unit test cho các functions

### 3.2 Inventory Views
**File**: `management/views/inventory.py`

**Views**:
- `inventory_list` (GET) - Danh sách tồn kho (phân trang 20, filter, search)
  - Staff: không thấy import_price
  - Manager: thấy import_price
- `inventory_low_stock` (GET) - Cảnh báo hàng sắp hết (chỉ Manager)

**Templates**: `templates/inventory/`
- `inventory_list.html` - Bảng tồn kho
  - Cột: Sản phẩm, Màu, Size, SKU, Tồn kho, Tồn tối thiểu, Giá bán, (Giá nhập - Manager only)
  - Cảnh báo: Nếu tồn < tối thiểu → nền đỏ hoặc icon ⚠️
  - Filter: Theo sản phẩm, size, màu
  - Search: Tên sản phẩm, SKU, mã

**Decorator**: `@staff_required` (staff & manager)

**Công việc**:
- [ ] Tạo inventory_list view
- [ ] Tạo inventory_low_stock view
- [ ] Tạo templates
- [ ] Thêm role check để ẩn import_price cho Staff
- [ ] Test filtering & searching

---

## Phase 4: Purchase Orders (Nhập hàng) - 2-3 ngày

### 4.1 Purchase Service
**File**: `management/services/purchase.py`

**Functions**:
- `create_purchase_order(supplier, items_data, user, notes='')` 
  - Tạo PurchaseOrder + Items
  - Cập nhật stock_quantity cho từng variant
  - Dùng `transaction.atomic()`
- `get_purchase_order_detail(order_id)`
- `update_purchase_order_status(order_id, status)` - waiting/finished/canceled

**Công việc**:
- [ ] Tạo purchase service
- [ ] Unit test

### 4.2 Purchase Order Views & Forms
**File**: `management/views/purchase.py` & `management/forms.py`

**Views**:
- `purchase_list` (GET) - Danh sách phiếu nhập (phân trang, filter nhà cung cấp, search)
- `purchase_create` (GET/POST) - Tạo phiếu nhập
  - Chọn nhà cung cấp
  - Thêm dòng chi tiết (HTMX: thêm/xóa dòng không reload)
  - Lưu → Tạo Order + cập nhật stock
- `purchase_detail` (GET) - Xem chi tiết phiếu nhập
- `purchase_edit` (GET/POST) - Sửa phiếu nhập (nếu status = waiting)
- `purchase_delete` (POST) - Hủy phiếu nhập

**Forms**:
- `PurchaseOrderForm` - supplier, notes
- `PurchaseOrderItemFormSet` - dynamic formset để thêm nhiều dòng

**Decorator**: `@manager_required`

**Templates**: `templates/purchase/`
- `purchase_list.html` - Bảng phiếu nhập
- `purchase_form.html` - Form tạo/sửa phiếu
  - Chọn nhà cung cấp
  - Inline formset cho chi tiết (HTMX thêm/xóa dòng)
  - Nút Lưu (tính tổng tiền tự động)
- `purchase_detail.html` - Xem chi tiết

**HTMX Integration**:
- Thêm dòng nhập: `hx-post="/purchase/add-item/" → swap dòng mới vào table`
- Xóa dòng: `hx-delete="/purchase/remove-item/{item_id}/" → xóa dòng khỏi table`
- Tìm sản phẩm: `hx-get="/products/search/?q={query}" → danh sách sản phẩm`

**Công việc**:
- [ ] Tạo purchase service
- [ ] Tạo PurchaseOrderForm & FormSet
- [ ] Tạo purchase views (list, create, detail, edit, delete)
- [ ] Tạo templates
- [ ] Tạo HTMX endpoints (add-item, remove-item, product-search)
- [ ] Test purchase order flow

---

## Phase 5: Sales Orders (Bán hàng) & POS - 3-4 ngày

### 5.1 Sales Service
**File**: `management/services/sales.py`

**Functions**:
- `create_sales_order(items_data, user, customer_name='', customer_phone='', payment_method='cash', payment_status='finished')`
  - Tạo SalesOrder + Items
  - Kiểm tra stock trước bán (raise error nếu không đủ)
  - Giảm stock_quantity cho từng variant
  - Dùng `transaction.atomic()`
- `calculate_profit(sale_order_item)` - Lợi nhuận = (selling_price_at_time - import_price) * qty
- `get_sales_order_detail(order_id)`

**Công việc**:
- [ ] Tạo sales service
- [ ] Unit test

### 5.2 POS (Point of Sale) Views & Forms
**File**: `management/views/sales.py`

**Views**:
- `pos_index` (GET) - Giao diện POS chính (tìm kiếm sản phẩm, giỏ hàng, checkout)
- `search_products` (GET) - HTMX: Tìm sản phẩm theo tên/mã → danh sách variants
- `add_to_cart` (POST) - HTMX: Thêm sản phẩm vào giỏ (lưu trong session hoặc client-side via Alpine.js)
- `remove_from_cart` (POST) - HTMX: Xóa sản phẩm khỏi giỏ
- `checkout` (POST) - Tạo SalesOrder từ giỏ hàng
- `sales_list` (GET) - Danh sách hóa đơn
  - Staff: chỉ thấy hóa đơn của mình
  - Manager: thấy tất cả
- `sales_detail` (GET) - Xem chi tiết hóa đơn
- `sales_print` (GET) - In hóa đơn (print-friendly HTML)

**Forms**:
- `SalesOrderForm` - customer_name (optional), customer_phone (optional), payment_method, payment_status

**Decorator**: 
- `pos_index`, `search_products`, `add_to_cart`, `remove_from_cart`, `checkout`: `@staff_required`
- `sales_list`, `sales_detail`, `sales_print`: `@staff_required` (với filter cho staff)

**Templates**: `templates/sales/`
- `pos.html` - Giao diện POS
  - Phần tìm kiếm (form + HTMX search)
  - Danh sách kết quả (variants)
  - Giỏ hàng (Alpine.js store)
    - Dòng: Sản phẩm, Size, Màu, Giá bán, Số lượng, Thành tiền, Nút xóa
    - Tổng tiền tự động tính
    - Nút "Xóa giỏ"
  - Form thanh toán (tên khách, SĐT, phương thức, nút Thanh toán)
  - Modal hoặc section riêng in hóa đơn sau khi tạo
- `sales_list.html` - Bảng danh sách hóa đơn (phân trang, search, filter)
- `sales_detail.html` - Chi tiết hóa đơn
- `sales_print.html` - In hóa đơn (print-friendly)
- `partials/product_search.html` - HTMX partial (danh sách kết quả tìm kiếm)
- `partials/cart_items.html` - HTMX partial (dòng giỏ hàng)

**Alpine.js Logic** (trong `static/js/pos.js`):
```javascript
// Cart store
x-data="{
  cart: [],
  totalAmount: 0,
  addItem(variant) { ... },
  removeItem(index) { ... },
  updateQuantity(index, qty) { ... },
  calculateTotal() { ... },
  clearCart() { ... }
}"
```

**HTMX Integration**:
- Tìm sản phẩm: `hx-get="/sales/search/?q={query}" → danh sách variants`
- Thêm giỏ: Dùng Alpine.js (client-side), submit form khi checkout
- Xóa từ giỏ: Alpine.js
- Checkout: `hx-post="/sales/checkout/" → xóa giỏ, tạo order, hiển thị hóa đơn`

**Công việc**:
- [ ] Tạo sales service
- [ ] Tạo search_products HTMX view
- [ ] Tạo POS layout với Alpine.js cart
- [ ] Tạo checkout view
- [ ] Tạo sales_list & sales_detail views
- [ ] Tạo sales_print view
- [ ] Tạo templates
- [ ] Tạo Alpine.js logic cho giỏ hàng
- [ ] Test POS flow end-to-end

---

## Phase 6: Reports & Analytics - 2-3 ngày

### 6.1 Reports Service
**File**: `management/services/reports.py`

**Functions**:
- `get_daily_stats(date)` - Thống kê 1 ngày (số đơn, doanh thu, lợi nhuận)
- `get_period_stats(date_from, date_to)` - Thống kê khoảng thời gian
- `get_top_products(date_from, date_to, limit=10)` - Top sản phẩm bán chạy
- `get_revenue_data(days=30)` - Dữ liệu doanh thu 30 ngày gần nhất (cho biểu đồ)
- `get_profit_data(days=30)` - Dữ liệu lợi nhuận 30 ngày gần nhất

**Công việc**:
- [ ] Tạo reports service
- [ ] Unit test

### 6.2 Dashboard & Reports Views
**File**: `management/views/dashboard.py`

**Views**:
- `dashboard` (GET) - Dashboard chính (Manager)
  - Thống kê hôm nay: Số đơn, tổng doanh thu, tổng lợi nhuận
  - Biểu đồ doanh thu 7 ngày gần nhất (Chart.js cột)
  - Biểu đồ top 5 sản phẩm bán chạy (Chart.js cột)
  - Cảnh báo hàng sắp hết (top 10 low-stock items)
- `reports_daily` (GET) - Báo cáo theo ngày (có date picker)
- `reports_period` (GET) - Báo cáo khoảng thời gian (date range picker)
- `reports_top_products` (GET) - Top sản phẩm bán chạy (date range, limit)

**Decorator**: `@manager_required`

**Templates**: `templates/dashboard/`
- `dashboard.html` - Dashboard chính
  - 4 card thống kê
  - 2 biểu đồ Chart.js
  - Table cảnh báo low-stock
- `reports_daily.html` - Báo cáo ngày
  - Date picker (Alpine.js)
  - Bảng thống kê
- `reports_period.html` - Báo cáo khoảng thời gian
  - Date range picker
  - Bảng thống kê
- `reports_top_products.html` - Top sản phẩm
  - Date range picker + limit input
  - Bảng + Biểu đồ cột

**Chart.js Integration** (trong template):
```html
<canvas id="chart-revenue"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
  new Chart(document.getElementById('chart-revenue'), {
    type: 'line',
    data: {{ chart_data|safe }},
    options: { ... }
  });
</script>
```

**Công việc**:
- [ ] Tạo reports service
- [ ] Tạo dashboard view
- [ ] Tạo reports views (daily, period, top-products)
- [ ] Tạo templates
- [ ] Tạo Chart.js visualizations
- [ ] Test reports accuracy

---

## Phase 7: Suppliers Management - 1-2 ngày

### 7.1 Supplier Views & Forms
**File**: `management/views/suppliers.py` & `management/forms.py`

**Views**:
- `supplier_list` (GET) - Danh sách nhà cung cấp (phân trang, search)
- `supplier_create` (GET/POST) - Tạo nhà cung cấp
- `supplier_edit` (GET/POST) - Sửa nhà cung cấp
- `supplier_delete` (POST) - Xóa nhà cung cấp

**Forms**:
- `SupplierForm` - name, phone, address

**Decorator**: `@manager_required`

**Templates**: `templates/suppliers/`
- `supplier_list.html` - Bảng danh sách
- `supplier_form.html` - Form thêm/sửa

**Công việc**:
- [ ] Tạo SupplierForm
- [ ] Tạo supplier views
- [ ] Tạo templates
- [ ] Test CRUD

---

## Phase 8: Admin & User Management - 1 ngày

### 8.1 Admin Interface
**File**: `management/admin.py`
- Tùy chỉnh Django Admin
- Thêm User, Group management
- Customize filters, search

### 8.2 User Management View (Optional)
**File**: `management/views/users.py`
- Manager tạo/sửa staff account
- Đặt password
- Assign groups

**Công việc**:
- [ ] Customize Django Admin
- [ ] (Optional) Tạo User management view

---

## Phase 9: Testing & Polish - 2-3 ngày

### 9.1 Unit & Integration Tests
**File**: `management/tests.py` hoặc `management/tests/`
- Test models
- Test services
- Test views
- Test forms
- Test permissions

**Công việc**:
- [ ] Viết tests cho models
- [ ] Viết tests cho services
- [ ] Viết tests cho views
- [ ] Viết tests cho permissions
- [ ] Đạt ≥ 80% coverage

### 9.2 UI/UX Polish
- Responsive design test trên mobile
- Xử lý loading states & error messages
- Notification system (Django messages framework)
- Input validation feedback

**Công việc**:
- [ ] Test responsive trên devices khác nhau
- [ ] Thêm loading spinners (Alpine.js)
- [ ] Thêm error handling
- [ ] Thêm success messages
- [ ] Test accessibility (WCAG)

### 9.3 Performance Optimization
- Database query optimization (select_related, prefetch_related)
- Pagination defaults
- Static file compression
- Caching (optional)

**Công việc**:
- [ ] Profile database queries
- [ ] Optimize slow queries
- [ ] Add caching if needed
- [ ] Minify CSS/JS

### 9.4 Documentation
- README.md (setup, run, deploy)
- API documentation (if needed)
- Code comments

**Công việc**:
- [ ] Write comprehensive README
- [ ] Add docstrings to functions
- [ ] Document assumptions & design decisions

---

## Phase 10: Deployment & DevOps - 1-2 ngày

### 10.1 Production Settings
- Set DEBUG = False
- Configure ALLOWED_HOSTS
- Set SECRET_KEY environment variable
- Configure logging
- Set up error tracking (Sentry optional)

### 10.2 Server Setup
- Install Gunicorn & Nginx (optional for MVP, can use Django's runserver for demo)
- Configure static files serving
- Configure media files serving
- SSL/HTTPS setup (optional)

### 10.3 Deployment Steps
- Requirements.txt finalization
- Database backup strategy
- Deployment checklist

**Công việc**:
- [ ] Finalize requirements.txt
- [ ] Create deployment guide
- [ ] Test production build locally
- [ ] Setup server (if needed for demo)

---

## Timeline Tổng cộng

| Phase | Mô tả | Thời gian | Người |
|-------|-------|----------|-------|
| 1 | Auth & Core Infrastructure | 3-4 ngày | Claude |
| 2 | Product Management | 3-4 ngày | Claude |
| 3 | Inventory Management | 2-3 ngày | Claude |
| 4 | Purchase Orders | 2-3 ngày | Claude |
| 5 | Sales & POS | 3-4 ngày | Claude |
| 6 | Reports & Analytics | 2-3 ngày | Claude |
| 7 | Suppliers Management | 1-2 ngày | Claude |
| 8 | Admin & User Mgmt | 1 ngày | Claude |
| 9 | Testing & Polish | 2-3 ngày | Claude |
| 10 | Deployment | 1-2 ngày | Claude |
| **TỔNG** | | **20-32 ngày** | |

**Ước tính thực tế**: 3-4 tuần làm việc liên tục (có thể chia thành sprint 2 tuần)

---

## Ưu tiên tính năng

### Must-Have (Yêu cầu bắt buộc)
1. ✅ Authentication (Login/Logout)
2. ✅ Product Management (CRUD)
3. ✅ Inventory Tracking
4. ✅ POS (Bán hàng)
5. ✅ Purchase Orders (Nhập hàng)
6. ✅ Reports (Doanh thu, Lợi nhuận)

### Nice-to-Have (Tính năng bổ sung)
1. Excel Import
2. Charts & Visualizations (Chart.js)
3. Low-stock Alerts
4. User Management UI
5. Advanced Filtering & Search

### Future (Phát triển sau)
1. Mobile app (React Native / Flutter)
2. Real-time notifications (WebSocket)
3. Warehouse management (multi-location)
4. Loyalty program
5. Accounting integration

---

## Risks & Mitigation

| Rủi ro | Mức độ | Giải pháp |
|--------|-------|----------|
| HTMX compatibility (old browsers) | Thấp | Fallback form POST; test trên modern browsers |
| Transaction race conditions | Trung bình | Dùng `transaction.atomic()` + database locks |
| Stock overselling | Cao | Service layer check stock trước bán; transaction |
| Performance với 300+ sản phẩm | Thấp | Pagination + select_related; test load |
| Image upload issues | Thấp | Validate size/format; test upload |
| User locks out after wrong password | Thấp | Django auth handles; test bruteforce protection |

---

## Notes & Assumptions

- Dùng **Django's built-in authentication** (không cần OAuth)
- Database là **MySQL** (`shoe_store`, root:1234)
- Frontend là **Django templates** + **Bootstrap 5** + **HTMX** + **Alpine.js** (không React)
- Charts dùng **Chart.js** (simple & lightweight)
- Không cần **REST API** (server-side rendering)
- **Staff không thấy giá nhập** (ẩn trong template & queryset filter)
- **Soft delete** dùng `is_active` flag (không xóa thật)
- **Transaction.atomic()** cho tất cả thao tác thay đổi tồn kho
- Deployment demo: Chạy trên `python manage.py runserver` (không yêu cầu Gunicorn/Nginx ngay)

---

## Checklist Before MVP Release

- [ ] All Phase 1-5 completed (Auth, Products, Inventory, Purchase, Sales)
- [ ] Phase 6 Dashboard (basic)
- [ ] Phase 9 Basic Testing (smoke tests)
- [ ] Phase 9 UI/UX Polish
- [ ] CLAUDE.md & README.md updated
- [ ] Database seed data working
- [ ] Both user accounts (staff/manager) working
- [ ] POS flow end-to-end tested
- [ ] No critical bugs
- [ ] Demo video/walkthrough ready

---

## Next Immediate Steps (Hôm nay/Ngày mai)

1. **Bắt đầu Phase 1**:
   - Tạo `management/permissions.py` → decorators
   - Tạo `management/views/auth.py` → Login/Logout views
   - Tạo `templates/auth/login.html`
   - Tạo `templates/base.html` → navbar + sidebar
   - Tạo `management/urls.py` → routing

2. **Kiểm tra**:
   - Đăng nhập thành công
   - Sidebar hiển thị đúng theo role
   - Logout hoạt động

---

## Reference Links

- Django Docs: https://docs.djangoproject.com/
- Bootstrap 5: https://getbootstrap.com/docs/5.0/
- HTMX: https://htmx.org/docs/
- Alpine.js: https://alpinejs.dev/
- Chart.js: https://www.chartjs.org/docs/latest/
