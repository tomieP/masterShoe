"""
Inventory Service - Business logic layer for stock management.

This module contains functions for checking, increasing, and decreasing stock quantities.
All stock-modifying operations use transaction.atomic() with select_for_update() to ensure
data consistency and prevent race conditions.

Usage:
    from management.services.inventory_service import (
        check_stock,
        increase_stock,
        decrease_stock,
        get_low_stock_variants,
        get_all_variants_stock,
        InsufficientStockError,
    )
"""

from decimal import Decimal
from typing import Optional
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError

from management.models import ProductVariant


class InsufficientStockError(Exception):
    """
    Exception raised when attempting to decrease stock but the requested quantity
    exceeds available stock.

    Attributes:
        variant_id: ID of the variant with insufficient stock
        requested: Quantity requested
        available: Available quantity
    """

    def __init__(self, variant_id: int, requested: int, available: int):
        self.variant_id = variant_id
        self.requested = requested
        self.available = available
        message = (
            f"Insufficient stock for variant {variant_id}: "
            f"requested {requested}, available {available}"
        )
        super().__init__(message)


class VariantNotFoundError(Exception):
    """
    Exception raised when a ProductVariant is not found or is inactive.

    Attributes:
        variant_id: ID of the variant that was not found
    """

    def __init__(self, variant_id: int):
        self.variant_id = variant_id
        super().__init__(f"ProductVariant with ID {variant_id} not found or is inactive")


def check_stock(variant_id: int, qty: int) -> bool:
    """
    Check if the specified variant has sufficient stock for the requested quantity.

    Args:
        variant_id: The ID of the ProductVariant to check.
        qty: The quantity to check against available stock.

    Returns:
        True if available stock >= requested quantity, False otherwise.

    Raises:
        VariantNotFoundError: If variant does not exist or is inactive.

    Examples:
        >>> check_stock(1, 5)
        True
        >>> check_stock(1, 100)
        False
    """
    if qty < 0:
        raise ValueError("Quantity must be a non-negative integer")

    try:
        variant = ProductVariant.objects.get(
            id=variant_id,
            is_active=True
        )
    except ProductVariant.DoesNotExist:
        raise VariantNotFoundError(variant_id)

    return variant.stock_quantity >= qty


def increase_stock(
    variant_id: int,
    qty: int,
    import_price: Optional[Decimal] = None
) -> ProductVariant:
    """
    Increase the stock quantity for a variant.

    This function uses transaction.atomic() with select_for_update() to ensure
    data consistency and prevent race conditions.

    Args:
        variant_id: The ID of the ProductVariant to update.
        qty: The quantity to add to current stock. Must be positive.
        import_price: Optional new import price to set. If None, no change.

    Returns:
        The updated ProductVariant instance.

    Raises:
        ValueError: If qty is not a positive integer.
        VariantNotFoundError: If variant does not exist or is inactive.

    Examples:
        >>> variant = increase_stock(1, 10)
        >>> variant.stock_quantity
        15
        >>> variant = increase_stock(1, 5, Decimal('150000.00'))
        >>> variant.import_price
        Decimal('150000.00')
    """
    if qty <= 0:
        raise ValueError("Quantity must be a positive integer")

    with transaction.atomic():
        # Lock the row for update to prevent race conditions
        try:
            variant = ProductVariant.objects.select_for_update().get(
                id=variant_id,
                is_active=True
            )
        except ProductVariant.DoesNotExist:
            raise VariantNotFoundError(variant_id)

        # Update stock quantity
        variant.stock_quantity = F('stock_quantity') + qty
        variant.save(update_fields=['stock_quantity', 'updated_at'])
        variant.refresh_from_db()

        # Update import price if provided
        if import_price is not None:
            if import_price < 0:
                raise ValueError("Import price cannot be negative")
            variant.import_price = import_price
            variant.save(update_fields=['import_price', 'updated_at'])

        return variant


def decrease_stock(variant_id: int, qty: int) -> ProductVariant:
    """
    Decrease the stock quantity for a variant (e.g., when a sale is made).

    This function uses transaction.atomic() with select_for_update() to ensure
    data consistency and prevent race conditions.

    IMPORTANT: This function raises InsufficientStockError if the requested quantity
    exceeds available stock. The caller MUST handle this exception.

    Args:
        variant_id: The ID of the ProductVariant to update.
        qty: The quantity to remove from current stock. Must be positive.

    Returns:
        The updated ProductVariant instance.

    Raises:
        ValueError: If qty is not a positive integer.
        VariantNotFoundError: If variant does not exist or is inactive.
        InsufficientStockError: If requested qty > available stock.

    Examples:
        >>> variant = decrease_stock(1, 3)
        >>> variant.stock_quantity
        12
        >>> decrease_stock(1, 100)  # Raises InsufficientStockError
    """
    if qty <= 0:
        raise ValueError("Quantity must be a positive integer")

    with transaction.atomic():
        # Lock the row for update to prevent race conditions
        try:
            variant = ProductVariant.objects.select_for_update().get(
                id=variant_id,
                is_active=True
            )
        except ProductVariant.DoesNotExist:
            raise VariantNotFoundError(variant_id)

        # Check if sufficient stock before decreasing
        if variant.stock_quantity < qty:
            raise InsufficientStockError(
                variant_id=variant_id,
                requested=qty,
                available=variant.stock_quantity
            )

        # Update stock quantity
        variant.stock_quantity = F('stock_quantity') - qty
        variant.save(update_fields=['stock_quantity', 'updated_at'])
        variant.refresh_from_db()

        return variant


def get_low_stock_variants(threshold: Optional[int] = None) -> list:
    """
    Get all active product variants where stock is below minimum quantity.

    Args:
        threshold: Optional custom threshold to override the variant's min_quantity.
                   If provided, returns variants where stock < threshold.
                   If None, uses each variant's min_quantity.

    Returns:
        List of ProductVariant objects where stock_quantity < min_quantity
        (or below custom threshold if provided).
        Variants are ordered by stock quantity (lowest first).

    Examples:
        >>> low_stock = get_low_stock_variants()
        >>> low_stock[0].product.name
        'Running Shoes'
        >>> low_stock = get_low_stock_variants(threshold=10)
    """
    variants = ProductVariant.objects.filter(is_active=True).select_related('product')

    if threshold is not None:
        # Use custom threshold for all variants
        variants = variants.filter(stock_quantity__lt=threshold)
    else:
        # Use each variant's min_quantity
        variants = variants.filter(stock_quantity__lt=F('min_quantity'))

    return list(variants.order_by('stock_quantity'))


def get_all_variants_stock() -> list:
    """
    Get all active product variants with stock information.

    Returns:
        List of all active ProductVariant objects, ordered by product name.
        Each variant includes stock_quantity and min_quantity for reference.

    Examples:
        >>> all_variants = get_all_variants_stock()
        >>> len(all_variants)
        196
        >>> all_variants[0].product.name
        'Air Max 90'
    """
    return list(
        ProductVariant.objects.filter(is_active=True)
        .select_related('product')
        .order_by('product__name', 'color', 'size')
    )
