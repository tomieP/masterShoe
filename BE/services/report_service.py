from typing import List, Dict, Optional

from BE.repositories.report_repository import ReportRepository
from BE.utils.logger import get_logger


class ReportService:
    """
    Service layer cho REPORT / ANALYTICS

    Nhiệm vụ:
    - Validate input
    - Gọi repository
    - Format response (nếu cần)
    - Log
    """

    def __init__(self, db_manager):
        self.repo = ReportRepository(db_manager)
        self.logger = get_logger(self.__class__.__name__)

    # =====================================================
    # 1. REVENUE
    # =====================================================
    def get_revenue(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> float:
        try:
            self.logger.info("Fetching revenue")

            # ===== VALIDATION =====
            if start_date and end_date and start_date > end_date:
                raise ValueError("start_date must be <= end_date")

            revenue = self.repo.get_revenue(start_date, end_date)

            self.logger.info(f"Revenue fetched: {revenue}")

            return revenue

        except Exception as e:
            self.logger.error(f"Get revenue failed: {str(e)}")
            raise

    # =====================================================
    # 2. TOP PRODUCTS
    # =====================================================
    def get_top_products(self, limit: int = 5) -> List[Dict]:
        try:
            self.logger.info(f"Fetching top products | limit={limit}")

            # ===== VALIDATION =====
            if limit <= 0:
                raise ValueError("limit must be > 0")

            data = self.repo.get_top_selling_products(limit)

            self.logger.info(f"Fetched {len(data)} top products")

            return data

        except Exception as e:
            self.logger.error(f"Get top products failed: {str(e)}")
            raise

    # =====================================================
    # 3. TOP VARIANTS (OPTIONAL)
    # =====================================================
    def get_top_variants(self, limit: int = 5) -> List[Dict]:
        try:
            self.logger.info(f"Fetching top variants | limit={limit}")

            if limit <= 0:
                raise ValueError("limit must be > 0")

            data = self.repo.get_top_selling_variants(limit)

            return data

        except Exception as e:
            self.logger.error(f"Get top variants failed: {str(e)}")
            raise

    # =====================================================
    # 4. PROFIT
    # =====================================================
    def get_profit(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> float:
        try:
            self.logger.info("Fetching profit")

            # ===== VALIDATION =====
            if start_date and end_date and start_date > end_date:
                raise ValueError("start_date must be <= end_date")

            profit = self.repo.get_profit(start_date, end_date)

            self.logger.info(f"Profit fetched: {profit}")

            return profit

        except Exception as e:
            self.logger.error(f"Get profit failed: {str(e)}")
            raise

    # =====================================================
    # 5. REVENUE BY DAY (CHART)
    # =====================================================
    def get_revenue_by_day(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        try:
            self.logger.info("Fetching revenue by day")

            if start_date and end_date and start_date > end_date:
                raise ValueError("start_date must be <= end_date")

            data = self.repo.get_revenue_by_day(start_date, end_date)

            return data

        except Exception as e:
            self.logger.error(f"Get revenue by day failed: {str(e)}")
            raise

    # =====================================================
    # 6. INVENTORY VALUE
    # =====================================================
    def get_inventory_value(self) -> float:
        try:
            self.logger.info("Fetching inventory value")

            value = self.repo.get_inventory_value()

            self.logger.info(f"Inventory value: {value}")

            return value

        except Exception as e:
            self.logger.error(f"Get inventory value failed: {str(e)}")
            raise

    # =====================================================
    # 7. DASHBOARD (COMBINE ALL)
    # =====================================================
    def get_dashboard(self) -> Dict:
        """
        API tổng hợp cho dashboard (frontend rất thích)
        """
        try:
            self.logger.info("Fetching dashboard data")

            revenue = self.repo.get_revenue()
            profit = self.repo.get_profit()
            top_products = self.repo.get_top_selling_products(5)
            inventory_value = self.repo.get_inventory_value()

            return {
                "revenue": revenue,
                "profit": profit,
                "top_products": top_products,
                "inventory_value": inventory_value
            }

        except Exception as e:
            self.logger.error(f"Get dashboard failed: {str(e)}")
            raise
