PRAGMA foreign_keys = ON;

-- PRODUCTS
CREATE TABLE products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    subtype TEXT,
    brand TEXT NOT NULL,
    description TEXT,
    image_url TEXT,
    is_active INTEGER DEFAULT 1 CHECK( is_active IN (0,1)),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

-- PRODUCTS VARIANTS
CREATE TABLE product_variants(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    color TEXT NOT NULL,
    size TEXT NOT NULL,
    price REAL NOT NULL CHECK(price > 0),
    cost REAL NOT NULL CHECK(cost > 0),
    sku TEXT UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(product_id) REFERENCES products(id)
);
-- INVENTORY
CREATE TABLE inventory(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    min_quantity INTEGER DEFAULT 5,
    updated_at TEXT,

    FOREIGN KEY(variant_id) REFERENCES product_variants(id)
);

-- INVOICES
CREATE TABLE invoices(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    user_id INTEGER,
    payment_method TEXT CHECK(payment_method IN ('cash','transfer')),
    payment_status TEXT CHECK(payment_status IN ('finished','owe')),
    note TEXT,
    total REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- INVOICE DETAILS
CREATE TABLE invoice_items(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    variant_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    price REAL NOT NULL,
    subtotal REAL,

    FOREIGN KEY(invoice_id) REFERENCES invoices(id),
    FOREIGN KEY(variant_id) REFERENCES product_variants(id)
);

-- IMPORT ORDERS
CREATE TABLE import_orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    supplier_name TEXT NOT NULL,
    status TEXT CHECK(status IN ('waiting','finished','canceled')),
    shipping_fee REAL DEFAULT 0,
    recieved_by INTEGER,
    recieved_at TEXT,
    note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(recieved_by) REFERENCES users(id)
);

-- IMPORT ITEMS
CREATE TABLE import_items(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_order_id INTEGER NOT NULL,
    variant_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    cost REAL NOT NULL,

    FOREIGN KEY(import_order_id) REFERENCES import_orders(id),
    FOREIGN KEY(variant_id) REFERENCES product_variants(id)
);

-- USERS
CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
    working_shift REAL,
    note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);
