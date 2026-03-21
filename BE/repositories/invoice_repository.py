from models.invoice import Invoice
from database.db import DatabaseManager

class InvoiceRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def _row_to_invoice(self, row):
        if row is None:
            return None
        return Invoice(
            id= row['id'],
            code= row['code'],
            user_id= row['user_id'],
            payment_method= row['payment_method'],
            payment_status= row['payment_status'],
            note= row['note'],
            total= row['total'],
            created_at= row['created_at']
        )
    
    #CREATE
    def create(self, invoice: Invoice):
        query = """
            INSERT INTO invoices(
            code, user_id, payment_method, payment_status, note, total, created_at
            )
            VALUES(?,?,?,?,?,?,?)
            """
        
        params = (
            invoice.code, invoice.user_id, invoice.payment_method, invoice.payment_status,
            invoice.note, invoice.total, invoice.created_at
        )

        invoice_id = self.db.execute_query(query, params, fetch=False)
        return invoice_id

    #GET BY ID
    def get_by_id(self, invoice_id: int):
        query = """
            SELECT * FROM invoices
            WHERE id = ?
            """
        
        params = (invoice_id,)
        rows = self.db.execute_query(query, params, fetch= True)

        if not rows:
            return None
        return self._row_to_invoice(rows[0])
    
    #GET ALL
    def get_all(self):
        query = """
            SELECT * FROM invoices
            ORDER BY created_at DESC
            """

        rows = self.db.execute_query(query)
        return [self._row_to_invoice(row) for row in rows]
    
    #UPDATE PAYMENT STATUS
    def update_payment_status(self, invoice_id: int, payment_status: str):
        query = """
            UPDATE invoices
            SET payment_status = ?
            WHERE id = ?
            """
        
        params = (payment_status, invoice_id)
        self.db.execute_query(query, params, fetch= False)
    
    #SOFT DELETE
    def delete(self, invoice_id: int):
        query = """
            UPDATE invoices
            SET is_active = 0
            WHERE id = ?
            """
        
        params = (invoice_id,)
        self.db.execute_query(query, params, fetch= False)