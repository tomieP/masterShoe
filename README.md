# MasterShoe - Hệ thống quản lý tiệm giày

Hệ thống quản lý bán hàng (POS), nhập hàng, sản phẩm đa biến thể và tồn kho cho tiệm giày/dép. Ứng dụng xây dựng bằng Django, giao diện Bootstrap 5, tương tác bằng HTMX + Alpine.js.

## Tính năng

- Bán hàng (POS): tìm kiếm sản phẩm, quản lý giỏ hàng, tạo hóa đơn, in hóa đơn
- Nhập hàng: quản lý phiếu nhập từ nhà cung cấp, cập nhật tồn kho
- Quản lý sản phẩm: sản phẩm đa biến thể (màu/size), hỗ trợ import Excel
- Tồn kho: theo dõi số lượng, cảnh báo sắp hết
- Báo cáo: doanh thu/lợi nhuận/top sản phẩm (Chart.js)
- Phân quyền: Staff (Nhân viên) và Manager (Quản lý)

## Công nghệ

- Backend: Django
- Database: MySQL
- Frontend: Bootstrap 5, HTMX, Alpine.js
- Thư viện: openpyxl (Excel), Pillow (Images)

## Cấu trúc thư mục

```text
C:\Proj\masterShoe\
├── shoe_store/           # Cấu hình dự án Django (settings, urls)
├── management/           # App chính quản lý cửa hàng
│   ├── views/            # View xử lý logic (chia theo domain)
│   ├── services/         # Business logic layer (inventory, sales)
│   ├── models.py         # Cấu trúc database
│   └── management/       # Custom commands (seed_data, import_excel)
├── templates/            # HTML templates (Django + HTMX + Alpine)
├── static/               # File tĩnh (CSS, JS, images)
├── media/                # Ảnh sản phẩm tải lên
├── manage.py             # Script quản lý Django
└── requirements.txt      # Danh sách thư viện
```

## Cài đặt (Windows)

```powershell
# tạo venv
python -m venv venv_django
.\venv_django\Scripts\activate

# cài deps
pip install -r requirements.txt
```

## Database

- MySQL cần có database `Mastershoe` (xem cấu hình trong `shoe_store/settings.py`).

```powershell
python manage.py migrate
python manage.py seed_data
```

## Chạy server

```powershell
python manage.py runserver
```

Mặc định: `http://127.0.0.1:8000/`

## Tài khoản mặc định

- Manager: `manager` / `123456`
- Staff: `staff` / `123456`

## Import sản phẩm từ Excel

Project có management command: `import_excel`.

```powershell
# import thật
python manage.py import_excel "C:\path\to\file.xlsx"

# thử trước, không ghi DB
python manage.py import_excel "C:\path\to\file.xlsx" --dry-run
```

Yêu cầu file `.xlsx` có header (hàng 1) đúng tên cột:

- `Tên`
- `Thương hiệu`
- `Size`
- `Màu`
- `Giá nhập`
- `Giá bán`
- `Tồn`

Ghi chú hành vi:

- Product match theo `(Tên, Thương hiệu)`.
- Variant match theo `(Màu, Size)`.
- Nếu variant đã tồn tại: cộng dồn `Tồn` vào `stock_quantity`.

## Reset database (xóa toàn bộ dữ liệu)

```powershell
python manage.py flush --no-input
```

Lệnh `flush` xóa toàn bộ data trong DB nhưng giữ nguyên cấu trúc bảng. Sau khi flush, chạy `seed_data` nếu muốn nạp lại dữ liệu mẫu:

```powershell
python manage.py seed_data
```

## Chạy tests

```powershell
# toàn bộ
python manage.py test

# theo app
python manage.py test management

# verbose
python manage.py test -v 2
```
