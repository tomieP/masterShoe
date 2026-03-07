import pytest
import os
from BE.database.db import DatabaseManager

# Setup a temporary database for testing
TEST_DB = "test_masterShoe.db"

@pytest.fixture
def db():
    # Initialize database manager with test path
    manager = DatabaseManager(db_path=TEST_DB)
    manager.init_database()
    yield manager
    # Cleanup after tests
    manager.close()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_add_product(db):
    query = """
        INSERT INTO products (
            code, name, type, brand
        ) VALUES (?, ?, ?, ?)
    """
    params = (
        "P001", "Product 1", "Type 1", "Brand 1"
    )
    
    product_id = db.excute_query(query, params, fetch=False)
    assert product_id is not None
    
    # Verify insertion
    result = db.excute_query("SELECT * FROM products WHERE id = ?", (product_id,))
    assert len(result) == 1
    assert result[0]['code'] == "P001"

def test_adjust_product(db):
    # First add a product
    query = """
        INSERT INTO products (
            code, name, type, brand
        ) VALUES (?, ?, ?, ?)
    """
    params = (
        "P001", "Product 1", "Type 1", "Brand 1"
    )
    db.excute_query(query, params, fetch=False)
    
    #changed name, type , brand
    query2 = """
        UPDATED products
        SET name = ?, type = ?, brand = ?
        WHERE code = ?;
    """
    params2 = (
        "Product 2", "Type 2", "Brand 2", "P001"
    )
    db.excute_query(query2, params2, fetch=False)
    

