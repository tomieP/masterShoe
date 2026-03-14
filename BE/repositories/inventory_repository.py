from models.inventory import Inventory
from database.db import DatabaseManager

class InventoryRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def _row_to_inventory(self, row):
        if row is None:
            return None
        return Inventory(
            id=row['id'],
            variant_id=row['variant_id'],
            quantity=row['quantity'],
            min_quantity=row['min_quantity'],
            updated_at=row['updated_at']
        )
    
    #CREATE
    def create(self, inventory: Inventory):
        query = """
            INSERT INTO inventory(
            variant_id, quantity, min_quantity, updated_at
            )
            VALUES(?,?,?,?)
            """
        params = (
            inventory.variant_id, inventory.quantity, inventory.min_quantity,
            inventory.updated_at
        )
        inventory_id =self.db.execute_query(query, params, fetch = False)
        return inventory_id
    
    #GET BY VARIANT
    def get_by_variant(self, variant_id: int):
        query = """
            SELECT * FROM inventory 
            WHERE variant_id = ?
        """
        params = (variant_id,)
        rows = self.db.execute_query(query, params, fetch = True)

        if rows is None or not rows:
            return None
        return self._row_to_inventory(rows[0])
    
    #UPDATE QUANTITY
    def update(self, variant_id: int, quantity: int):
        query = """
            UPDATE inventory
            SET quantity = ?, updated_at = CURRENT_TIMESTAMP
            WHERE variant_id = ?
            """
        params = (quantity, variant_id)
        self.db.execute_query(query, params, fetch = False)
    
    #INCREASE STOCK
    def increase_stock(self, variant_id: int, amount: int):
        query = """
            UPDATE inventory
            SET quantity = quantity + ?
            updated_at = CURRENT_TIMESTAMP
            WHERE variant_id = ?
            """
        params = (amount, variant_id)
        self.db.execute_query(query, params, fetch = False)

   #DECREASE STOCK
    def decrease_stock(self, variant_id: int, amount: int):
        query = """
            UPDATE inventory
            SET quantity = quantity - ?
            updated_at = CURRENT_TIMESTAMP
            WHERE variant_id = ?
            """
        params = (amount, variant_id)
        self.db.execute_query(query, params, fetch = False)
    