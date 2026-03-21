from models.invoice_detail import InvoiceDetail
from database.db import DatabaseManager

class InvoiceDetailRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_invoice_detail(self, row):
        if row is None:
            return None
        return InvoiceDetail(
            id=row['id'],
            invoice_id=row['invoice_id'],
            variant_id=row['variant_id'],
            quantity=row['quantity'],
            price=row['price']
        )
    
    #GET BY ID
    def get_by_id(self, item_id: int):
        query = """
            SELECT * FROM invoice_items
            WHERE id = ?
        """
        params = (item_id,)
        rows = self.db.execute_query(query, params, fetch=True)

        if not rows:
            return None
        return self._row_to_invoice_detail(rows[0])
    
    #GET BY INVOICE
    def get_by_invoice(self, invoice_id: int):
        query = """
            SELECT * FROM invoice_items
            WHERE invoice_id = ?
        """
        rows = self.db.execute_query(query, (invoice_id,), fetch=True)

        return [self._row_to_invoice_detail(row) for row in rows]

    #CREATE
    def create(self, item: InvoiceDetail):
        query = """
            INSERT INTO invoice_items (
                invoice_id, variant_id, quantity, price
            )
            VALUES (?, ?, ?, ?)
        """
        params = (
            item.invoice_id,
            item.variant_id,
            item.quantity,
            item.price,
        )

        item_id = self.db.execute_query(query, params, fetch=False)
        return item_id
    
    #DELETE BY INVOICE (rarely used)
    def delete_by_invoice(self, invoice_id: int):
        query = """
            DELETE FROM invoice_items
            WHERE invoice_id = ?
        """
        self.db.execute_query(query, (invoice_id,), fetch=False)

    # DELETE SINGLE ITEM (rare)
    def delete(self, item_id: int):
        query = """
            DELETE FROM invoice_items
            WHERE id = ?
        """
        self.db.execute_query(query, (item_id,), fetch=False)