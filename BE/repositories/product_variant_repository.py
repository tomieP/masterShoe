from models.product_variant import ProductVariant
from database.db import DatabaseManager

class VariantRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
    def _row_to_variant(self, row):
        if row is None:
            return None
        return ProductVariant(
            id = row['id'],
            product_id= row['product_id'],
            size= row['size'],
            color= row['color'],
            price= row['price'],
            cost= row['cost'],
            sku= row['sku'],
            is_active= row['is_active'],
            created_at= row['created_at'],
            updated_at= row['updated_at']
        )

    #GET BY ID
    def get_by_id(self, variant_id: int):
        query = """
            SELECT * FROM product_variants WHERE id = ?
        """
        params = (variant_id,)
        rows = self.db.execute_query(query, params, fetch= True)

        if not rows:
            return None
        return self._row_to_variant(rows[0])
    
    #GET BY SKU
    def get_by_sku(self, sku_id: str):
        query ="""
            SELECT * FROM product_variants
            WHERE sku = ?
            """
        params = (sku_id,)
        rows = self.db.execute_query(query, params, fetch = True)

        if not rows:
            return None
        return self._row_to_variant(rows[0])
    

    #GET BY PRODUCT
    def get_by_product(self, product_id: int):
        query = """
            SELECT * FROM product_variants 
            WHERE product_id = ?
            ORDER BY size ASC
            """
        params = (product_id,)
        rows = self.db.execute_query(query, params, fetch = True)
        return [self._row_to_variant(row) for row in rows]

    #CREATE
    def create(self, variant: ProductVariant):
        query = """
            INSERT INTO product_variants(
            product_id, size, color, price, cost, sku, is_active, created_at
            )
            VALUES(?,?,?,?,?,?,?,?)
            """
        params = (
            variant.product_id, variant.size, variant.color, variant.price,
            variant.cost, variant.sku, variant.created_at
        )
        variant_id = self.db.execute_query(query, params, fetch = False)
        return variant_id

    #UPDATE
    def update(self, variant: ProductVariant):
        query = """
            UPDATE product_variants
            SET product_id = ?, size = ?, color = ?, price = ?,
            cost = ?, sku = ?, is_active = ?, created_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
        params = (
            variant.product_id, variant.size, variant.color,
            variant.price, variant.cost, variant.sku, variant.is_active, variant.created_at,
            variant.id
        )
        self.db.execute_query(query, params, fetch=False)
    
    #SOFT DELETE 
    def delete(self, variant_id: int):
        query = """
            UPDATE product_variants
            SET is_active = 0
            WHERE id = ?            
        """
        params = (variant_id,)
        self.db.execute_query(query, params, fetch = False)
   
