from datetime import datetime
from typing import List, Dict

from models.invoice import Invoice
from models.invoice_detail import InvoiceDetail

from repositories.invoice_repository import InvoiceRepository
from repositories.invoice_detail_repository import InvoiceDetailRepository
from repositories.product_variant_repository import VariantRepository
from repositories.inventory_repository import InventoryRepository
from repositories.product_repository import ProductRepository

from utils.logger import get_logger


class OrderService:
    def __init__(self, db_manager):
        self.db = db_manager

        self.product_repo = ProductRepository(db_manager)
        self.invoice_repo = InvoiceRepository(db_manager)
        self.invoice_detail_repo = InvoiceDetailRepository(db_manager)
        self.variant_repo = VariantRepository(db_manager)
        self.inventory_repo = InventoryRepository(db_manager)

        self.logger = get_logger(self.__class__.__name__)

    #CREATE ORDER
    def create_order(
        self,
        items: List[Dict],  # [{variant_id, quantity}]
        payment_method: str = "cash",
        user_id: int = None,
        note: str = None
    ) -> int:

        try:
            self.logger.info("Creating order...")

            # ===== VALIDATION =====
            if not items:
                raise ValueError("Order must have at least 1 item")

            if payment_method not in ["cash", "transfer"]:
                raise ValueError("Invalid payment method")

            conn = self.db.connection
            conn.execute("BEGIN")

            total = 0
            processed_items = []

            # =========================================
            # STEP 1: VALIDATE + PREPARE DATA
            # =========================================
            for item in items:
                variant_id = item["variant_id"]
                quantity = item["quantity"]

                if quantity <= 0:
                    raise ValueError("Quantity must be > 0")

                variant = self.variant_repo.get_by_id(variant_id)
                if not variant:
                    raise ValueError(f"Variant {variant_id} not found")

                inventory = self.inventory_repo.get_by_variant(variant_id)
                if not inventory:
                    raise ValueError(f"Inventory not found for variant {variant_id}")

                if inventory.quantity < quantity:
                    raise ValueError(f"Not enough stock for variant {variant_id}")

                price = variant.price
                subtotal = price * quantity
                total += subtotal

                processed_items.append({
                    "variant_id": variant_id,
                    "quantity": quantity,
                    "price": price
                })

            # =========================================
            # STEP 2: CREATE INVOICE
            # =========================================
            invoice = Invoice(
                code=f"INV-{int(datetime.now().timestamp())}",
                user_id=user_id,
                payment_method=payment_method,
                payment_status="finished",
                note=note,
                total=total,
                created_at=datetime.now()
            )

            invoice_id = self.invoice_repo.create(invoice)

            # =========================================
            # STEP 3: CREATE INVOICE DETAILS + UPDATE STOCK
            # =========================================
            for item in processed_items:
                detail = InvoiceDetail(
                    invoice_id=invoice_id,
                    variant_id=item["variant_id"],
                    quantity=item["quantity"],
                    price=item["price"]
                )

                self.invoice_detail_repo.create(detail)

                # giảm kho
                self.inventory_repo.decrease_stock(
                    item["variant_id"],
                    item["quantity"]
                )

            # =========================================
            # COMMIT
            # =========================================
            conn.commit()

            self.logger.info(f"Order created successfully: {invoice_id}")

            return invoice_id

        except Exception as e:
            self.logger.error(f"Create order failed: {str(e)}")

            if self.db.connection:
                self.db.connection.rollback()

            raise
    
    def get_order_detail(self, invoice_id: int):
        try:
            self.logger.info(f"Fetching order detail: {invoice_id}")

            # =========================================
            # STEP 1: GET INVOICE
            # =========================================
            invoice = self.invoice_repo.get_by_id(invoice_id)

            if not invoice or not invoice.is_active:
                raise ValueError("Invoice not found")

            # =========================================
            # STEP 2: GET DETAILS
            # =========================================
            details = self.invoice_detail_repo.get_by_invoice(invoice_id)

            items = []

            # =========================================
            # STEP 3: BUILD ITEMS
            # =========================================
            for d in details:
                variant = self.variant_repo.get_by_id(d.variant_id)

                if not variant:
                    continue  # skip nếu dữ liệu lỗi

                # optional: lấy product
                product = None
                if variant.product_id:
                    product = self.product_repo.get_by_id(variant.product_id)

                subtotal = d.quantity * d.price

                items.append({
                    "variant_id": variant.id,
                    "product_id": variant.product_id,

                    "product_name": product.name if product else None,
                    "brand": product.brand if product else None,

                    "size": variant.size,
                    "color": variant.color,

                    "quantity": d.quantity,
                    "price": d.price,
                    "subtotal": subtotal
                })

            # =========================================
            # STEP 4: BUILD RESPONSE
            # =========================================
            result = {
                "invoice": {
                    "id": invoice.id,
                    "code": invoice.code,
                    "user_id": invoice.user_id,
                    "payment_method": invoice.payment_method,
                    "payment_status": invoice.payment_status,
                    "note": invoice.note,
                    "total": invoice.total,
                    "created_at": invoice.created_at
                },
                "items": items,
                "total": invoice.total
            }

            return result

        except Exception as e:
            self.logger.error(f"Get order detail failed: {str(e)}")
            raise

    def get_all_orders(
        self,
        page: int = 1,
        page_size: int = 10,
        payment_method: str = None,
        payment_status: str = None,
        start_date: str = None,
        end_date: str = None
    ):
        try:
            self.logger.info("Fetching orders list")

            # ===== VALIDATION =====
            if page <= 0:
                raise ValueError("Page must be > 0")

            if page_size <= 0:
                raise ValueError("Page size must be > 0")

            offset = (page - 1) * page_size

            # =========================================
            # STEP 1: GET DATA
            # =========================================
            invoices = self.invoice_repo.get_all_with_filter(
                offset=offset,
                limit=page_size,
                payment_method=payment_method,
                payment_status=payment_status,
                start_date=start_date,
                end_date=end_date
            )

            # =========================================
            # STEP 2: COUNT TOTAL
            # =========================================
            total = self.invoice_repo.count_with_filter(
                payment_method=payment_method,
                payment_status=payment_status,
                start_date=start_date,
                end_date=end_date
            )

            # =========================================
            # STEP 3: BUILD RESPONSE
            # =========================================
            data = []

            for inv in invoices:
                data.append({
                    "id": inv.id,
                    "code": inv.code,
                    "user_id": inv.user_id,
                    "payment_method": inv.payment_method,
                    "payment_status": inv.payment_status,
                    "total": inv.total,
                    "created_at": inv.created_at
                })

            total_pages = (total + page_size - 1) // page_size

            return {
                "data": data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages
                }
            }

        except Exception as e:
            self.logger.error(f"Get all orders failed: {str(e)}")
            raise