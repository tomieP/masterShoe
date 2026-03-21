PRAGMA foreign_keys = ON;

-- PRODUCTS
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    subtype TEXT,
    brand TEXT,
    description TEXT,
    image_url TEXT,
    is_active INTEGER DEFAULT 1 CHECK( is_active IN (0,1)),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- PRODUCTS VARIANTS
CREATE TABLE IF NOT EXISTS product_variants(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    color TEXT NOT NULL,
    size TEXT NOT NULL,
    price REAL NOT NULL CHECK(price > 0),
    cost REAL NOT NULL CHECK(cost > 0),
    sku TEXT UNIQUE NOT NULL,
    is_active INTEGER DEFAULT 1 CHECK( is_active IN (0,1)),    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(product_id, color, size),

    FOREIGN KEY(product_id) REFERENCES products(id)
    ON DELETE CASCADE
);
-- INVENTORY
CREATE TABLE IF NOT EXISTS inventory(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    min_quantity INTEGER DEFAULT 5 CHECK (min_quantity >= 0),
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(variant_id) REFERENCES product_variants(id)
    ON DELETE CASCADE
    UNIQUE(variant_id)
);

-- INVOICES
CREATE TABLE IF NOT EXISTS invoices(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    user_id INTEGER,
    payment_method TEXT CHECK(payment_method IN ('cash','transfer')),
    payment_status TEXT DEFAULT 'finished' CHECK(payment_status IN ('finished','owe')),
    note TEXT,
    total REAL,
    is_active INTEGER DEFAULT 1 CHECK( is_active IN (0,1)),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- INVOICE DETAILS
CREATE TABLE IF NOT EXISTS invoice_items(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    variant_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    price REAL NOT NULL CHECK (price >= 0),

    FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
    FOREIGN KEY(variant_id) REFERENCES product_variants(id)
);

-- IMPORT ORDERS
CREATE TABLE IF NOT EXISTS import_orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    supplier_name TEXT NOT NULL,
    status TEXT DEFAULT 'waiting' CHECK(status IN ('waiting','finished','canceled')),
    shipping_fee REAL DEFAULT 0,
    recieved_by INTEGER,
    recieved_at TEXT,
    note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(recieved_by) REFERENCES users(id)
);

-- IMPORT ITEMS
CREATE TABLE IF NOT EXISTS import_items(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_order_id INTEGER NOT NULL,
    variant_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    cost REAL NOT NULL CHECK (cost >= 0),

    FOREIGN KEY(import_order_id) REFERENCES import_orders(id) ON DELETE CASCADE,
    FOREIGN KEY(variant_id) REFERENCES product_variants(id)
);

-- USERS
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
    working_shift REAL,
    note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
/*CREATE INDEX idx_product_variants_product_id
ON product_variants(product_id);

CREATE INDEX idx_inventory_variant_id
ON inventory(variant_id);

CREATE INDEX idx_invoice_items_invoice_id
ON invoice_items(invoice_id);

CREATE INDEX idx_invoice_items_variant_id
ON invoice_items(variant_id);

CREATE INDEX idx_import_items_order_id
ON import_items(import_order_id);*/
