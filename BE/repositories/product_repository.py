from models.product import Product
from database.db import DatabaseManager

class ProductRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
    def _row_to_product(self, row):
        if row is None:
            return None
        
        return Product(
            id = row['id'],
            code= row['code'],
            name = row['name'],
            type = row['type'],
            subtype = row['subtype'],
            brand= row['brand'],
            description= row['description'],
            image_url= row['image_url'],
            is_active= row['is_active'],
            created_at= row['created_at'],
            updated_at= row['updated_at']
        )
    
    def get_by_id(self, product_id: int):
        query = """
            SELECT * FROM products WHERE id = ?
        """
        params = (product_id,)
        rows = self.db.execute_query(query, params)

        if not rows:
            return None
        return self._row_to_product(rows[0])   

    #CREATE
    def create(self, product: Product):
        query = """
            INSERT INTO products (
            code, name, type, subtype, brand, description,
            image_url, is_active, created_at, updated_at
            )
            VALUES(?,?,?,?,?,?,?,?,?,?)
        """
        params = (
            product.code, product.name, product.type, product.subtype,
            product.brand, product.description, product.image_url,
            product.is_active, product.created_at, product.updated_at
        )
        product_id = self.db.execute_query(query, params, fetch = False)
        return product_id
    
    #GET ALL
    def get_all(self):

        query = """
        SELECT *
        FROM products
        ORDER BY created_at DESC
        """

        rows = self.db.execute_query(query)

        return [self._row_to_product(row) for row in rows]
    
    #UPDATE
    def update(self, product: Product):
        query = """
            UPDATE products
            SET 
            code = ?, name = ?, type = ?, subtype = ?, brand = ?,
            description = ?, image_url = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        params = (product.code, product.name, product.type, product.subtype,
                  product.brand, product.description, product.image_url,
                  int(product.is_active), product.id)
        self.db.execute_query(query, params, fetch = False)

    #SOFT DELETE
    def deactive(self, product_id: int):
        query = """
            UPDATE products
            SET is_active = 0
            WHERE id =?
            """
        params = (product_id,)
        self.db.execute_query(query, params, fetch= False)

    #SEARCH BY CODE
    def search_by_code(self, code: str):
        query ="""
            SELECT * FROM products
            WHERE code = ?
            """
        rows = self.db.execute_query(query, (code,), fetch = True)

        if not rows:
            return None
        return self._row_to_product(rows[0])

