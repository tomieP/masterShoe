# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview
This repository contains a Django web application for managing a shoe store (Quản lý Tiệm Giày). The application includes:
- Product and variant management
- Inventory tracking (stock quantities)
- Purchase orders (nhập hàng) from suppliers
- Sales orders (bán hàng) at the point of sale
- Reporting and statistics
- Role-based access control (Staff and Manager)

The project has been migrated from a FastAPI backend to a full-stack Django application with Bootstrap 5, HTMX, and Alpine.js for the frontend.

## Development Commands

### Setup
```bash
# Clone the repository and navigate to the project root
cd C:\Proj\masterShoe

# Create and activate a virtual environment (if not already present)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Ensure MySQL is running and the database 'shoe_store' exists with user 'root' and password '1234'
# (See settings.py for database configuration)

# Apply migrations
python manage.py migrate

# Create a superuser (optional, as we have predefined staff/manager accounts)
# python manage.py createsuperuser

# Load sample data (if needed)
python manage.py seed_data

# Start the development server
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

### Predefined Accounts
- **Staff**: username=`staff`, password=`123456` (access to sales, inventory, and order history)
- **Manager**: username=`manager`, password=`123456` (full access including reports, product management, purchase orders, etc.)

### Running Tests
```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test management

# Run tests with verbose output
python manage.py test -v 2
```

### Other Useful Commands
```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files (for production)
python manage.py collectstatic

# Check for any issues in the project
python manage.py check

# Start a Django shell
python manage.py shell

# Run the seed data command to populate sample data
python manage.py seed_data
```

## Code Architecture

### Project Structure
```
C:\Proj\masterShoe\
├── shoe_store/                 # Django project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py             # Project settings (database, media, static, etc.)
│   ├── urls.py                 # Root URL routing
│   └── wsgi.py
├── management/                 # Main Django app
│   ├── __init__.py
│   ├── admin.py                # Django Admin customization
│   ├── apps.py
│   ├── models.py               # Database models (Product, Variant, Supplier, Orders, etc.)
│   ├── views/                  # View functions (organized by functionality)
│   │   ├── __init__.py
│   │   ├── auth.py             # Login, logout views
│   │   ├── dashboard.py        # Dashboard and reports (manager only)
│   │   ├── inventory.py        # Inventory management
│   │   ├── products.py         # Product and variant management
│   │   ├── purchase.py         # Purchase orders (nhập hàng)
│   │   ├── sales.py            # Sales orders (bán hàng) - POS
│   │   └── suppliers.py        # Supplier management
│   ├── services/               # Business logic layer (optional but used)
│   │   ├── __init__.py
│   │   ├── inventory.py        # Inventory service (stock checks, updates)
│   │   ├── purchase.py         # Purchase service
│   │   ├── sales.py            # Sales service
│   │   └── reports.py          # Reporting service
│   ├── forms.py                # Django forms for validation
│   ├── permissions.py          # Custom permission decorators
│   ├── tests.py                # Tests
│   ├── urls.py                 # App-level URL routing
│   └── management/             # Custom management commands
│       ├── __init__.py
│       └── commands/
│           ├── __init__.py
│           └── seed_data.py    # Command to load sample data
├── templates/                  # HTML templates (Bootstrap 5 + HTMX + Alpine.js)
│   ├── base.html               # Base template with navbar and sidebar
│   ├── auth/                   # Login, logout templates
│   ├── dashboard/              # Dashboard and charts
│   ├── inventory/              # Inventory views
│   ├── products/               # Product management views
│   ├── purchase/               # Purchase order views
│   ├── sales/                  # POS and sales views
│   ├── suppliers/              # Supplier management views
│   └── partials/               # HTMX partial templates (e.g., product search, cart items)
├── static/                     # Static files (CSS, JavaScript, images)
│   ├── css/                    # Custom CSS
│   ├── js/                     # Alpine.js logic and custom JS
│   └── lib/                    # Third-party libraries (Bootstrap, Chart.js, HTMX via CDN or local)
├── media/                      # Uploaded product images
├── requirements.txt            # Python dependencies
├── manage.py                   # Django management script
├── db.sqlite3                  # SQLite database (if using SQLite instead of MySQL)
└── CLAUDE.md                   # This file
```

### Key Components

#### Models (`management/models.py`)
- **Supplier**: Nhà cung cấp (name, phone, address)
- **Product**: Sản phẩm (code, name, brand, image, description, type, subtype, is_active)
- **ProductVariant**: Biến thể sản phẩm (linked to Product, color, size, import_price, selling_price, sku, stock_quantity, min_quantity, is_active)
- **PurchaseOrder**: Đơn nhập hàng (supplier, date, total, status, created_by)
- **PurchaseOrderItem**: Chi tiết đơn nhập (variant, quantity, actual_import_price)
- **SalesOrder**: Hóa đơn bán hàng (customer info, date, total, payment method/status, created_by)
- **SalesOrderItem**: Chi tiết hóa đơn (variant, quantity, selling_price_at_time)

#### Views (`management/views/`)
Views are organized by functionality:
- **auth.py**: Login, logout
- **dashboard.py**: Dashboard with statistics and charts (Chart.js) - Manager only
- **products.py**: Product CRUD, variant management, Excel import
- **purchase.py**: Purchase order creation and management
- **sales.py**: Point of Sale (POS) interface, cart management, order creation
- **inventory.py**: Inventory viewing, low-stock alerts
- **suppliers.py**: Supplier CRUD

#### Templates (`templates/`)
- Base template (`base.html`) includes:
  - Responsive Navbar (collapsible on mobile)
  - Sidebar with role-based navigation (Staff sees Sales, Inventory, Order History; Manager sees all menus)
  - Uses Bootstrap 5 for styling
  - Includes HTMX for AJAX requests (e.g., live product search, updating cart without full page reload)
  - Includes Alpine.js for client-side interactivity (e.g., toggling dropdowns, managing temporary cart state)
  - Includes Chart.js for rendering reports and dashboards
- Partial templates in `partials/` are used with HTMX to update specific parts of the page (e.g., product search results, cart items).

#### Services (`management/services/`)
Optional layer for business logic to keep views thin:
- `inventory_service.py`: Functions for checking stock, increasing/decreasing stock, low stock alerts.
- `sales_service.py`: Functions for creating sales orders, calculating profits, updating stock.
- `purchase_service.py`: Functions for creating purchase orders, updating stock from imports.
- `reports_service.py`: Functions for generating sales reports, profit calculations, chart data.

#### Forms (`forms.py`)
Django forms for validation and rendering (used with Bootstrap styling via `crispy-forms` or manual rendering).

#### Permissions (`permissions.py`)
Custom decorators for role-based access:
- `@login_required`: Requires authentication
- `@staff_required`: Allows access for staff and manager
- `@manager_required`: Allows access for manager only
- `@manager_or_staff_required`: Allows access for either role (used for sales and inventory)

#### URLs
- Root URL configuration in `shoe_store/urls.py` includes the management app URLs.
- Each view group has its own URL patterns in `management/urls.py`.

#### Static and Media Files
- Static files (CSS, JS, images) are served from `/static/` (defined in `settings.py`).
- User-uploaded product images are stored in `/media/products/` and served from `/media/`.

#### Database
- Configured to use MySQL (database: `shoe_store`, user: `root`, password: `1234`). 
- For development, you can switch to SQLite by commenting/uncommenting the database block in `settings.py`.
- Run `python manage.py migrate` to create tables.
- Sample data can be loaded with `python manage.py seed_data`.

## Common Development Tasks

### Adding a New Feature (e.g., a new report)
1. **Model**: If new data is needed, add a field to an existing model or create a new model in `models.py`, then run `makemigrations` and `migrate`.
2. **Service**: Add a function in the relevant service file (e.g., `reports_service.py`) to encapsulate the logic.
3. **View**: Add a view function in the appropriate view file (e.g., `views/reports.py` or extend an existing one) that uses the service and renders a template.
4. **Template**: Create an HTML template in `templates/reports/` (or reuse an existing one) to display the report.
5. **URL**: Add a URL pattern in `management/urls.py` mapping to the new view.
6. **Navigation**: If the report should be accessible from the menu, add a link in the sidebar in `base.html` (considering role-based visibility).
7. **Permissions**: Apply the appropriate permission decorator to the view (e.g., `@manager_required`).

### Modifying the Database Schema
1. Edit `models.py` to reflect the desired changes (add/remove fields, change relationships, etc.).
2. Run `python manage.py makemigrations` to generate a migration file.
3. Review the migration file to ensure it correctly captures the changes.
4. Run `python manage.py migrate` to apply the changes to the database.
5. If needed, update any related forms, views, or services to handle the new schema.

### Styling and Frontend Adjustments
- The base styling uses Bootstrap 5. Custom CSS can be added in `static/css/`.
- For interactive components (modals, dropdowns, form validations), use Alpine.js (already included).
- For dynamic content updates without full page reloads (e.g., searching products, updating cart), use HTMX:
  - Add `hx-get`, `hx-post`, `hx-trigger`, `hx-target`, etc., attributes to HTML elements.
  - The view should return either a full page render (for initial load) or a partial template (for HTMX swaps) based on the request headers (HTMX sends `HX-Request: true`).
- JavaScript logic specific to the application can be placed in `static/js/`.

### Testing
- Unit tests should be placed in `tests.py` or in a `tests/` directory within the app.
- Use Django's TestCase for testing models, views, and forms.
- Run tests frequently with `python manage.py test`.

### Deployment Notes
- For production, set `DEBUG = False` in `settings.py`.
- Configure allowed hosts (`ALLOWED_HOSTS`) appropriately.
- Use a production WSGI server (e.g., Gunicorn) and a reverse proxy (e.g., Nginx).
- Collect static files with `python manage.py collectstatic`.
- Ensure media files are served securely and efficiently.
- Set up proper logging and error monitoring.

## Important Notes
- The application uses Django's built-in authentication system. Passwords are hashed securely.
- All forms include CSRF protection by default.
- Database queries use Django ORM, which helps prevent SQL injection.
- The `stock_quantity` field on `ProductVariant` is updated automatically when creating/purchasing or selling via the services (using `transaction.atomic` for consistency).
- Staff users cannot see the `import_price` field (cost price) in the inventory or product views; this is restricted in the templates and queries.
- Manager users have access to all features, including reports, product management, purchase orders, and user management (via Django Admin or custom views).
- The predefined accounts (`staff`/`manager`) are created via the `seed_data` command or can be created manually.

## Troubleshooting
- **Database connection errors**: Verify MySQL is running, the database exists, and the credentials in `settings.py` are correct.
- **Migration errors**: Check the migration files for correctness; sometimes you may need to fake an initial migration if the database already has tables (`python manage.py migrate --fake`).
- **Static files not loading**: Ensure `DEBUG=True` or that you have run `collectstatic` and configured your web server to serve static files.
- **Image upload issues**: Verify that the `MEDIA_ROOT` and `MEDIA_URL` settings are correct and that the web server has write permissions to the media directory.
- **Permission denied errors**: Ensure you are logged in with the correct account and that the view has the appropriate permission decorator.
