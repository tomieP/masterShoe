from typing import List, Dict, Optional
from BE.database.db import DatabaseManager




class ReportRepository:
    """
    Repository chuyên xử lý REPORT / ANALYTICS

    NOTE:
    - Chỉ READ (SELECT)
    - Query phức tạp (JOIN, GROUP BY)
    - Không dùng model (return dict để flexible)
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    # =====================================================
    # 1. REVENUE (DOANH THU)
    # =====================================================
    def get_revenue(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> float:

        query = """
            SELECT SUM(total) AS revenue
            FROM invoices
            WHERE is_active = 1
        """

        params = []

        if start_date:
            query += " AND created_at >= ?"
            params.append(start_date)

        if end_date:
            query += " AND created_at <= ?"
            params.append(end_date)

        rows = self.db.execute_query(query, tuple(params))

        if not rows or rows[0]["revenue"] is None:
            return 0.0

        return float(rows[0]["revenue"])

    # =====================================================
    # 2. TOP SELLING PRODUCTS
    # =====================================================
    def get_top_selling_products(self, limit: int = 5) -> List[Dict]:

        query = """
            SELECT 
                p.id AS product_id,
                p.name AS product_name,
                p.brand,
                SUM(ii.quantity) AS total_sold,
                SUM(ii.quantity * ii.price) AS revenue
            FROM invoice_items ii
            JOIN product_variants pv ON ii.variant_id = pv.id
            JOIN products p ON pv.product_id = p.id
            JOIN invoices i ON ii.invoice_id = i.id
            WHERE i.is_active = 1
            GROUP BY p.id, p.name, p.brand
            ORDER BY total_sold DESC
            LIMIT ?
        """

        rows = self.db.execute_query(query, (limit,))

        if not rows:
            return []

        return [dict(row) for row in rows]

    # =====================================================
    # 3. TOP SELLING VARIANTS (OPTIONAL)
    # =====================================================
    def get_top_selling_variants(self, limit: int = 5) -> List[Dict]:

        query = """
            SELECT 
                pv.id AS variant_id,
                p.name AS product_name,
                pv.size,
                pv.color,
                SUM(ii.quantity) AS total_sold,
                SUM(ii.quantity * ii.price) AS revenue
            FROM invoice_items ii
            JOIN product_variants pv ON ii.variant_id = pv.id
            JOIN products p ON pv.product_id = p.id
            JOIN invoices i ON ii.invoice_id = i.id
            WHERE i.is_active = 1
            GROUP BY pv.id, p.name, pv.size, pv.color
            ORDER BY total_sold DESC
            LIMIT ?
        """

        rows = self.db.execute_query(query, (limit,))

        if not rows:
            return []

        return [dict(row) for row in rows]

    # =====================================================
    # 4. PROFIT (LỢI NHUẬN)
    # =====================================================
    def get_profit(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> float:

        query = """
            SELECT 
                SUM(ii.quantity * (ii.price - pv.cost)) AS profit
            FROM invoice_items ii
            JOIN product_variants pv ON ii.variant_id = pv.id
            JOIN invoices i ON ii.invoice_id = i.id
            WHERE i.is_active = 1
        """

        params = []

        if start_date:
            query += " AND i.created_at >= ?"
            params.append(start_date)

        if end_date:
            query += " AND i.created_at <= ?"
            params.append(end_date)

        rows = self.db.execute_query(query, tuple(params))

        if not rows or rows[0]["profit"] is None:
            return 0.0

        return float(rows[0]["profit"])

    # =====================================================
    # 5. REVENUE BY DAY (CHART)
    # =====================================================
    def get_revenue_by_day(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:

        query = """
            SELECT 
                DATE(created_at) AS date,
                SUM(total) AS revenue
            FROM invoices
            WHERE is_active = 1
        """

        params = []

        if start_date:
            query += " AND created_at >= ?"
            params.append(start_date)

        if end_date:
            query += " AND created_at <= ?"
            params.append(end_date)

        query += """
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """

        rows = self.db.execute_query(query, tuple(params))

        if not rows:
            return []

        return [dict(row) for row in rows]

    # =====================================================
    # 6. INVENTORY VALUE (GIÁ TRỊ TỒN KHO)
    # =====================================================
    def get_inventory_value(self) -> float:

        query = """
            SELECT 
                SUM(i.quantity * pv.cost) AS inventory_value
            FROM inventory i
            JOIN product_variants pv ON i.variant_id = pv.id
        """

        rows = self.db.execute_query(query)

        if not rows or rows[0]["inventory_value"] is None:
            return 0.0

        return float(rows[0]["inventory_value"])
