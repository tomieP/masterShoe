"""
Sales Service - Business logic layer for sales management.

This module contains functions for creating sales orders, calculating profits,
and retrieving order details. All operations that modify stock or create orders
use transaction.atomic() to ensure data consistency.

Usage:
    from management.services.sales import (
        create_sales_order,
        calculate_profit,
        get_sales_order_detail,
    )
"""

import uuid
from decimal import Decimal
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from management.models import SalesOrder, SalesOrderItem, ProductVariant
from management.services.inventory_service import decrease_stock, InsufficientStockError, VariantNotFoundError


def generate_sales_order_code() -> str:
    """Generates a unique sales order code: HD-YYYYMMDD-XXXX"""
    now = timezone.now()
    date_str = now.strftime("%Y%m%d")
    random_suffix = str(uuid.uuid4().hex[:4]).upper()
    return f"HD-{date_str}-{random_suffix}"


def create_sales_order(
    items_data: List[Dict[str, Any]],
    user: User,
    customer_name: str = '',
    customer_phone: str = '',
    payment_method: str = 'cash',
    payment_status: str = 'finished'
) -> SalesOrder:
    """
    Creates a SalesOrder and its items, updates stock quantities.

    Args:
        items_data: List of dicts, each with 'variant_id' and 'quantity'.
        user: The User instance (seller).
        customer_name: Optional customer name.
        customer_phone: Optional customer phone.
        payment_method: 'cash' or 'transfer'.
        payment_status: 'finished' or 'owe'.

    Returns:
        The created SalesOrder instance.

    Raises:
        ValueError: If items_data is empty or contains invalid data.
        InsufficientStockError: If any variant has insufficient stock.
        VariantNotFoundError: If any variant ID is invalid or inactive.
    """
    if not items_data:
        raise ValueError("Sales order must contain at least one item")

    with transaction.atomic():
        # 1. Create the SalesOrder instance first
        order = SalesOrder.objects.create(
            code=generate_sales_order_code(),
            customer_name=customer_name,
            customer_phone=customer_phone,
            created_by=user,
            payment_method=payment_method,
            payment_status=payment_status,
            total_amount=Decimal('0.00')
        )

        total_amount = Decimal('0.00')

        # 2. Process each item
        for item in items_data:
            variant_id = item.get('variant_id')
            quantity = item.get('quantity')

            if not variant_id or not isinstance(quantity, int) or quantity <= 0:
                raise ValueError(f"Invalid item data: {item}")

            # Get variant to retrieve its current selling price
            # Note: decrease_stock already does select_for_update()
            try:
                variant = ProductVariant.objects.get(id=variant_id, is_active=True)
            except ProductVariant.DoesNotExist:
                raise VariantNotFoundError(variant_id)

            # 3. Decrease stock (this handles transaction/locking)
            decrease_stock(variant_id, quantity)

            # 4. Create Order Item
            item_total = Decimal(str(variant.selling_price)) * quantity
            SalesOrderItem.objects.create(
                sales_order=order,
                variant=variant,
                quantity=quantity,
                selling_price_at_time=variant.selling_price
            )

            total_amount += item_total

        # 5. Update total amount
        order.total_amount = total_amount
        order.save(update_fields=['total_amount', 'updated_at'])

        return order


def calculate_profit(sale_order_item: SalesOrderItem) -> Decimal:
    """
    Calculates profit for a specific sales order item.
    Profit = (selling_price_at_time - import_price) * quantity
    """
    import_price = sale_order_item.variant.import_price
    selling_price = sale_order_item.selling_price_at_time
    qty = sale_order_item.quantity

    return (selling_price - import_price) * qty


def get_sales_order_detail(order_id: int) -> SalesOrder:
    """
    Retrieves a SalesOrder with all its items and related data.
    """
    return get_object_or_404(
        SalesOrder.objects.prefetch_related(
            'items',
            'items__variant',
            'items__variant__product'
        ).select_related('created_by'),
        id=order_id
    )
