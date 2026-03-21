from datetime import datetime

from repositories.inventory_repository import InventoryRepository
from utils.logger import get_logger


class InventoryService:
    def __init__(self, db_manager):
        self.db = db_manager
        self.inventory_repo = InventoryRepository(db_manager)
        self.logger = get_logger(self.__class__.__name__)

    # GET INVENTORY
    def get_inventory(self, variant_id: int):
        inventory = self.inventory_repo.get_by_variant(variant_id)

        if not inventory:
            raise ValueError("Inventory not found")

        return inventory

    # INCREASE STOCK (IMPORT / RESTOCK)
    def increase_stock(self, variant_id: int, amount: int):
        try:
            self.logger.info(f"Increasing stock | variant={variant_id}, amount={amount}")

            # ===== VALIDATION =====
            if amount <= 0:
                raise ValueError("Amount must be positive")

            inventory = self.inventory_repo.get_by_variant(variant_id)
            if not inventory:
                raise ValueError("Inventory not found")

            # ===== UPDATE =====
            self.inventory_repo.increase_stock(variant_id, amount)

            self.logger.info("Stock increased successfully")

        except Exception as e:
            self.logger.error(f"Increase stock failed: {str(e)}")
            raise

    # DECREASE STOCK (SELL / EXPORT)
    def decrease_stock(self, variant_id: int, amount: int):
        try:
            self.logger.info(f"Decreasing stock | variant={variant_id}, amount={amount}")

            # ===== VALIDATION =====
            if amount <= 0:
                raise ValueError("Amount must be positive")

            inventory = self.inventory_repo.get_by_variant(variant_id)
            if not inventory:
                raise ValueError("Inventory not found")

            if inventory.quantity < amount:
                raise ValueError("Not enough stock")

            # ===== UPDATE =====
            self.inventory_repo.decrease_stock(variant_id, amount)

            self.logger.info("Stock decreased successfully")

        except Exception as e:
            self.logger.error(f"Decrease stock failed: {str(e)}")
            raise

    # SET STOCK (MANUAL ADJUST)
    def set_stock(self, variant_id: int, quantity: int):
        try:
            self.logger.info(f"Setting stock | variant={variant_id}, quantity={quantity}")

            if quantity < 0:
                raise ValueError("Quantity cannot be negative")

            inventory = self.inventory_repo.get_by_variant(variant_id)
            if not inventory:
                raise ValueError("Inventory not found")

            self.inventory_repo.update(variant_id, quantity)

            self.logger.info("Stock updated successfully")

        except Exception as e:
            self.logger.error(f"Set stock failed: {str(e)}")
            raise

    # CHECK LOW STOCK
    def is_low_stock(self, variant_id: int) -> bool:
        inventory = self.inventory_repo.get_by_variant(variant_id)

        if not inventory:
            raise ValueError("Inventory not found")

        return inventory.quantity <= inventory.min_quantity

    # CHECK OUT OF STOCK
    def is_out_of_stock(self, variant_id: int) -> bool:
        inventory = self.inventory_repo.get_by_variant(variant_id)

        if not inventory:
            raise ValueError("Inventory not found")

        return inventory.quantity == 0

    # SAFE DECREASE (TRANSACTION)
    # dùng khi có order
    def safe_decrease_stock(self, variant_id: int, amount: int):
        try:
            self.logger.info(f"[TX] Safe decrease | variant={variant_id}, amount={amount}")

            conn = self.db.connection
            conn.execute("BEGIN")

            inventory = self.inventory_repo.get_by_variant(variant_id)

            if not inventory:
                raise ValueError("Inventory not found")

            if inventory.quantity < amount:
                raise ValueError("Not enough stock")

            self.inventory_repo.decrease_stock(variant_id, amount)

            conn.commit()

            self.logger.info("[TX] Stock decreased successfully")

        except Exception as e:
            self.logger.error(f"[TX] Decrease failed: {str(e)}")

            if self.db.connection:
                self.db.connection.rollback()

            raise