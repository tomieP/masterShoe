from datetime import datetime
from typing import List

from BE.models.product import Product
from BE.models.product_variant import ProductVariant
from BE.models.inventory import Inventory

from BE.repositories.product_repository import ProductRepository
from BE.repositories.product_variant_repository import VariantRepository
from BE.repositories.inventory_repository import InventoryRepository

from BE.database.db import DatabaseManager

from BE.dtos.product_dto import ProductDTO, VariantDTO, InventoryDTO
from BE.utils.logger import get_logger


class ProductService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.product_repo = ProductRepository(db_manager)
        self.variant_repo = VariantRepository(db_manager)
        self.inventory_repo = InventoryRepository(db_manager)

        self.logger = get_logger(self.__class__.__name__)

    # CREATE PRODUCT FULL (TRANSACTION)
    def create_product_full(self, product: Product, variants: List[ProductVariant]) -> int:
        try:
            self.logger.info(f"Creating product: {product.code}")

            # =====PRODUCT VALIDATION =====
            if not product.code:
                raise ValueError("Product code is required")

            if not product.name:
                raise ValueError("Product name is required")

            existing = self.product_repo.search_by_code(product.code)
            if existing:
                raise ValueError("Product code already exists")

            # ===== BEGIN TRANSACTION =====
            conn = self.db.connection
            conn.execute("BEGIN")

            # ===== CREATE PRODUCT =====
            product.created_at = datetime.now()
            product.updated_at = datetime.now()
            product_id = self.product_repo.create(product)

            # ===== CREATE VARIANTS + INVENTORY =====
            for v in variants:
                # ===== VARIANT VALIDATION =====
                if v.price <= 0:
                    raise ValueError("Variant price must be > 0")

                existing_sku = self.variant_repo.get_by_sku(v.sku)
                if existing_sku:
                    raise ValueError("Variant SKU already exists")

                v.product_id = product_id
                v.created_at = datetime.now()
                v.updated_at = datetime.now()

                variant_id = self.variant_repo.create(v)

                inventory = Inventory(
                    variant_id=variant_id,
                    quantity=0,
                    min_quantity=5,
                    updated_at=datetime.now()
                )

                self.inventory_repo.create(inventory)

            # ===== COMMIT =====
            conn.commit()
            self.logger.info(f"Product created successfully: {product_id}")

            return product_id

        except Exception as e:
            self.logger.error(f"Create product failed: {str(e)}")

            if self.db.connection:
                self.db.connection.rollback()

            raise

    # GET PRODUCT DETAIL (DTO)
    def get_product_detail(self, product_id: int) -> ProductDTO:
        self.logger.info(f"Fetching product detail: {product_id}")

        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        variants = self.variant_repo.get_by_product(product_id)

        variant_dtos = []

        for v in variants:
            inventory = self.inventory_repo.get_by_variant(v.id)

            inventory_dto = InventoryDTO(
                quantity=inventory.quantity if inventory else 0,
                min_quantity=inventory.min_quantity if inventory else 0
            )

            variant_dto = VariantDTO(
                id=v.id,
                size=v.size,
                color=v.color,
                price=v.price,
                cost=v.cost,
                sku=v.sku,
                inventory=inventory_dto
            )

            variant_dtos.append(variant_dto)

        return ProductDTO(
            id=product.id,
            code=product.code,
            name=product.name,
            type=product.type,
            brand=product.brand,
            variants=variant_dtos
        )

    # UPDATE PRODUCT
    def update_product(self, product_id: int, update_data: dict):
        try:
            self.logger.info(f"Updating product: {product_id}")

            # =====PRODUCT VALIDATION=====
            if not product_id:
                raise ValueError("Product ID is required")

            existing = self.product_repo.get_by_id(product_id)
            if not existing:
                raise ValueError("Product not found")

            # =====BEGIN TRANSACTION=====
            conn = self.db.connection
            conn.execute("BEGIN")

            # =====UPDATE PRODUCT=====
            for key, value in update_data.items():
                setattr(existing, key, value)

            existing.updated_at = datetime.now()

            self.product_repo.update(existing)
            # ====== COMMIT =====
            conn.commit()
            self.logger.info(f"Product updated successfully: {existing.id}")

        except Exception as e:
            self.logger.error(f"Update product failed: {str(e)}")

            if self.db.connection:
                self.db.connection.rollback()
                
            raise

    # =========================================
    # SOFT DELETE
    # =========================================
    def deactivate_product(self, product_id: int):
        self.logger.info(f"Deactivating product: {product_id}")

        try:
            # =====PRODUCT VALIDATION=====
            existing = self.product_repo.get_by_id(product_id)
            
            if not existing:
                raise ValueError("Product not found")
            
            # =====BEGIN TRANSACTION=====
            conn = self.db.connection
            conn.execute("BEGIN")
        
            # =====DEACTIVE PRODUCT=====
            self.product_repo.deactive(product_id)

            # =====COMMIT=====
            conn.commit()
            self.logger.info(f"Product deactivated successfully: {product_id}")

        except Exception as e:
            self.logger.error(f"Deactivate product failed: {str(e)}")

            if self.db.connection:
                self.db.connection.rollback()
            raise