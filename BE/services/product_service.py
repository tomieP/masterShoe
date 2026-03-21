from datetime import datetime
from typing import List

from models.product import Product
from models.product_variant import ProductVariant
from models.inventory import Inventory

from repositories.product_repository import ProductRepository
from repositories.product_variant_repository import VariantRepository
from repositories.inventory_repository import InventoryRepository

from dtos.product_dto import ProductDTO, VariantDTO, InventoryDTO
from utils.logger import get_logger


class ProductService:
    def __init__(self, db_manager):
        self.db = db_manager
        self.product_repo = ProductRepository(db_manager)
        self.variant_repo = VariantRepository(db_manager)
        self.inventory_repo = InventoryRepository(db_manager)

        self.logger = get_logger(self.__class__.__name__)

    # CREATE PRODUCT FULL (TRANSACTION)
    def create_product_full(self, product: Product, variants: List[ProductVariant]) -> int:
        try:
            self.logger.info(f"Creating product: {product.code}")

            # ===== VALIDATION =====
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
            product_id = self.product_repo.create(product)

            # ===== CREATE VARIANTS + INVENTORY =====
            for v in variants:
                if v.price <= 0:
                    raise ValueError("Variant price must be > 0")

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
    def update_product(self, product: Product):
        self.logger.info(f"Updating product: {product.id}")

        if not product.id:
            raise ValueError("Product ID is required")

        existing = self.product_repo.get_by_id(product.id)
        if not existing:
            raise ValueError("Product not found")

        self.product_repo.update(product)

    # =========================================
    # SOFT DELETE
    # =========================================
    def deactivate_product(self, product_id: int):
        self.logger.info(f"Deactivating product: {product_id}")

        self.product_repo.deactive(product_id)