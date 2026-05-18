"""
Purchase Service - Business logic layer for managing purchase orders.

This module handles the creation, retrieval, and status updates of purchase orders,
ensuring that stock levels are correctly updated in coordination with the inventory service.
"""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.db.models import Sum

from management.models import Supplier, ProductVariant, PurchaseOrder, PurchaseOrderItem
from management.services.inventory_service import increase_stock, decrease_stock, VariantNotFoundError


class PurchaseOrderError(Exception):
    """Base exception for purchase order operations."""
    pass


def create_purchase_order(
    supplier: Supplier,
    items_data: List[Dict[str, Any]],
    user: Any,
    notes: str = '',
    status: str = 'waiting'
) -> PurchaseOrder:
    """
    Create a new PurchaseOrder with items and update stock if finished.

    Args:
        supplier: Supplier instance.
        items_data: List of dictionaries, each containing:
            - 'variant': ProductVariant instance or ID
            - 'quantity': int
            - 'price': Decimal (actual import price)
        user: User instance who created the order.
        notes: Optional notes string.
        status: initial status ('waiting' or 'finished').

    Returns:
        The created PurchaseOrder instance.

    Raises:
        ValueError: If items_data is empty or invalid data provided.
        PurchaseOrderError: If variant lookup fails.
    """
    if not items_data:
        raise ValueError("Purchase order must have at least one item.")

    with transaction.atomic():
        # 1. Create the Purchase Order object
        # Note: Code generation logic can be added here or in model save()
        # For simplicity, we assume the code is generated or passed
        import uuid
        order_code = f"PO-{uuid.uuid4().hex[:8].upper()}"

        order = PurchaseOrder.objects.create(
            code=order_code,
            supplier=supplier,
            notes=notes,
            created_by=user,
            status=status,
            total_amount=0 # Will update after adding items
        )

        total_amount = Decimal('0.00')

        # 2. Create items and track total
        for item in items_data:
            variant = item['variant']
            if isinstance(variant, int):
                try:
                    variant = ProductVariant.objects.get(id=variant)
                except ProductVariant.DoesNotExist:
                    raise PurchaseOrderError(f"Variant ID {item['variant']} not found.")

            qty = item['quantity']
            price = Decimal(str(item['price']))

            if qty <= 0:
                raise ValueError(f"Quantity for variant {variant.sku} must be positive.")
            if price < 0:
                raise ValueError(f"Price for variant {variant.sku} cannot be negative.")

            PurchaseOrderItem.objects.create(
                purchase_order=order,
                variant=variant,
                quantity=qty,
                actual_import_price=price
            )

            total_amount += qty * price

            # 3. Update stock if status is 'finished'
            if status == 'finished':
                increase_stock(variant.id, qty, import_price=price)

        # 4. Update total amount
        order.total_amount = total_amount
        order.save(update_fields=['total_amount'])

        return order


def get_purchase_order_detail(order_id: int) -> PurchaseOrder:
    """
    Retrieve a purchase order with its items pre-fetched.
    """
    try:
        return PurchaseOrder.objects.select_related('supplier', 'created_by').prefetch_related('items__variant__product').get(id=order_id)
    except PurchaseOrder.DoesNotExist:
        raise PurchaseOrderError(f"PurchaseOrder with ID {order_id} not found.")


def update_purchase_order_status(order_id: int, new_status: str) -> PurchaseOrder:
    """
    Update purchase order status and handle stock transitions.

    waiting -> finished: Increase stock
    finished -> canceled: Decrease stock (revert)
    waiting -> canceled: No change
    """
    if new_status not in dict(PurchaseOrder.STATUS_CHOICES):
        raise ValueError(f"Invalid status: {new_status}")

    with transaction.atomic():
        order = PurchaseOrder.objects.select_for_update().get(id=order_id)
        old_status = order.status

        if old_status == new_status:
            return order

        # Transition logic
        if old_status == 'waiting' and new_status == 'finished':
            # Increase stock for all items
            for item in order.items.all():
                increase_stock(item.variant.id, item.quantity, import_price=item.actual_import_price)

        elif old_status == 'finished' and new_status == 'canceled':
            # Revert stock (Decrease)
            for item in order.items.all():
                # Note: This might raise InsufficientStockError if someone already sold these
                decrease_stock(item.variant.id, item.quantity)

        elif old_status == 'canceled':
            raise PurchaseOrderError("Cannot update status of a canceled order.")

        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])

        return order
