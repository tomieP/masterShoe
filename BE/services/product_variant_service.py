from datetime import datetime
from typing import List

from models.product_variant import ProductVariant
from models.inventory import Inventory

from repositories.product_repository import ProductRepository
from repositories.product_variant_repository import VariantRepository
from repositories.inventory_repository import InventoryRepository

from utils.logger import get_logger


class VariantService:
    def __init__(self, db_manager):
        self.db = db_manager

        self.product_repo = ProductRepository(db_manager)
        self.variant_repo = VariantRepository(db_manager)
        self.inventory_repo = InventoryRepository(db_manager)

        self.logger = get_logger(self.__class__.__name__)

    # CREATE VARIANT (WITH INVENTORY)
    def create_variant(self, variant: ProductVariant) -> int:
        try:
            self.logger.info(f"Creating variant for product={variant.product_id}")

            # ===== VALIDATION =====
            if not variant.product_id:
                raise ValueError("product_id is required")

            product = self.product_repo.get_by_id(variant.product_id)
            if not product:
                raise ValueError("Product not found")

            if variant.price <= 0:
                raise ValueError("Price must be > 0")

            if variant.cost < 0:
                raise ValueError("Cost cannot be negative")

            # ===== TRANSACTION =====
            conn = self.db.connection
            conn.execute("BEGIN")

            # ===== CREATE VARIANT =====
            variant.created_at = datetime.now()
            variant_id = self.variant_repo.create(variant)

            # ===== CREATE INVENTORY =====
            inventory = Inventory(
                variant_id=variant_id,
                quantity=0,
                min_quantity=5,
                updated_at=datetime.now()
            )

            self.inventory_repo.create(inventory)

            conn.commit()

            self.logger.info(f"Variant created successfully: {variant_id}")

            return variant_id

        except Exception as e:
            self.logger.error(f"Create variant failed: {str(e)}")

            if self.db.connection:
                self.db.connection.rollback()

            raise

    # GET VARIANT
    def get_variant(self, variant_id: int) -> ProductVariant:
        variant = self.variant_repo.get_by_id(variant_id)

        if not variant:
            raise ValueError("Variant not found")

        return variant

    # GET ALL VARIANTS BY PRODUCT
    def get_variants_by_product(self, product_id: int) -> List[ProductVariant]:
        product = self.product_repo.get_by_id(product_id)

        if not product:
            raise ValueError("Product not found")

        return self.variant_repo.get_by_product(product_id)

    # UPDATE VARIANT
    def update_variant(self, variant: ProductVariant):
        try:
            self.logger.info(f"Updating variant: {variant.id}")

            if not variant.id:
                raise ValueError("Variant ID is required")

            existing = self.variant_repo.get_by_id(variant.id)
            if not existing:
                raise ValueError("Variant not found")

            if variant.price <= 0:
                raise ValueError("Price must be > 0")

            if variant.cost < 0:
                raise ValueError("Cost cannot be negative")

            self.variant_repo.update(variant)

            self.logger.info("Variant updated successfully")

        except Exception as e:
            self.logger.error(f"Update variant failed: {str(e)}")
            raise

    # DELETE VARIANT (WITH INVENTORY)
    def delete_variant(self, variant_id: int):
        try:
            self.logger.info(f"Deleting variant: {variant_id}")

            variant = self.variant_repo.get_by_id(variant_id)
            if not variant:
                raise ValueError("Variant not found")

            # ===== TRANSACTION =====
            conn = self.db.connection
            conn.execute("BEGIN")

            self.variant_repo.delete(variant_id)

            conn.commit()

            self.logger.info("Variant deleted successfully")

        except Exception as e:
            self.logger.error(f"Delete variant failed: {str(e)}")

            if self.db.connection:
                self.db.connection.rollback()

            raise

    # BULK CREATE VARIANTS
    def create_variants_bulk(self, product_id: int, variants: List[ProductVariant]):
        try:
            self.logger.info(f"Bulk creating variants for product={product_id}")

            product = self.product_repo.get_by_id(product_id)
            if not product:
                raise ValueError("Product not found")

            conn = self.db.connection
            conn.execute("BEGIN")

            created_ids = []

            for v in variants:
                if v.price <= 0:
                    raise ValueError("Price must be > 0")

                v.product_id = product_id
                v.created_at = datetime.now()

                variant_id = self.variant_repo.create(v)

                inventory = Inventory(
                    variant_id=variant_id,
                    quantity=0,
                    min_quantity=5,
                    updated_at=datetime.now()
                )

                self.inventory_repo.create(inventory)

                created_ids.append(variant_id)

            conn.commit()

            self.logger.info(f"Bulk created {len(created_ids)} variants")

            return created_ids

        except Exception as e:
            self.logger.error(f"Bulk create failed: {str(e)}")

            if self.db.connection:
                self.db.connection.rollback()

            raise