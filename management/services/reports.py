"""
Reports Service - Business logic for generating sales reports and analytics.

This module contains functions for generating sales statistics, revenue data,
and product performance metrics for dashboard and reporting views.

Usage:
    from management.services.reports import (
        get_daily_stats,
        get_period_stats,
        get_top_products,
        get_revenue_data,
        get_profit_data,
    )
"""

from decimal import Decimal
from datetime import timedelta, date, datetime, time
from typing import Dict, List, Any
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import TruncDate
from django.utils import timezone

from management.models import SalesOrder, SalesOrderItem


def get_daily_stats(target_date: date) -> Dict[str, Any]:
    """
    Get sales statistics for a single day.

    Args:
        target_date: The date to get stats for (datetime.date object).

    Returns:
        Dict with keys:
        - order_count: Number of sales orders
        - revenue: Total revenue (Decimal)
        - profit: Total profit (Decimal)

    Example:
        >>> get_daily_stats(date(2026, 5, 6))
        {'order_count': 5, 'revenue': Decimal('500000.00'), 'profit': Decimal('100000.00')}
    """
    # Create timezone-aware datetime bounds for the target date
    start_dt = timezone.make_aware(datetime.combine(target_date, time.min))
    end_dt = timezone.make_aware(datetime.combine(target_date, time.max))

    # Filter sales orders for the specific date
    orders = SalesOrder.objects.filter(
        sale_date__gte=start_dt,
        sale_date__lte=end_dt
    )

    # Count orders
    order_count = orders.count()

    # Sum revenue
    revenue_data = orders.aggregate(
        total_revenue=Sum('total_amount')
    )
    revenue = revenue_data['total_revenue'] or Decimal('0.00')

    # Calculate profit: sum of (selling_price - import_price) * quantity
    profit_data = SalesOrderItem.objects.filter(
        sales_order__sale_date__gte=start_dt,
        sales_order__sale_date__lte=end_dt
    ).select_related('variant').aggregate(
        total_profit=Sum(
            (F('selling_price_at_time') - F('variant__import_price')) * F('quantity'),
            output_field=DecimalField()
        )
    )
    profit = profit_data['total_profit'] or Decimal('0.00')

    return {
        'order_count': order_count,
        'revenue': revenue,
        'profit': profit,
    }


def get_period_stats(date_from: date, date_to: date) -> Dict[str, Any]:
    """
    Get sales statistics for a date range.

    Args:
        date_from: Start date (inclusive).
        date_to: End date (inclusive).

    Returns:
        Dict with keys:
        - order_count: Number of sales orders
        - revenue: Total revenue (Decimal)
        - profit: Total profit (Decimal)

    Example:
        >>> get_period_stats(date(2026, 5, 1), date(2026, 5, 7))
        {'order_count': 35, 'revenue': Decimal('3500000.00'), 'profit': Decimal('700000.00')}
    """
    # Create timezone-aware datetime bounds
    start_dt = timezone.make_aware(datetime.combine(date_from, time.min))
    end_dt = timezone.make_aware(datetime.combine(date_to, time.max))

    # Filter sales orders for the date range
    orders = SalesOrder.objects.filter(
        sale_date__gte=start_dt,
        sale_date__lte=end_dt
    )

    # Count orders
    order_count = orders.count()

    # Sum revenue
    revenue_data = orders.aggregate(
        total_revenue=Sum('total_amount')
    )
    revenue = revenue_data['total_revenue'] or Decimal('0.00')

    # Calculate profit
    profit_data = SalesOrderItem.objects.filter(
        sales_order__sale_date__gte=start_dt,
        sales_order__sale_date__lte=end_dt
    ).select_related('variant').aggregate(
        total_profit=Sum(
            (F('selling_price_at_time') - F('variant__import_price')) * F('quantity'),
            output_field=DecimalField()
        )
    )
    profit = profit_data['total_profit'] or Decimal('0.00')

    return {
        'order_count': order_count,
        'revenue': revenue,
        'profit': profit,
    }


def get_top_products(
    date_from: date,
    date_to: date,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get top-selling products by quantity in a date range.

    Args:
        date_from: Start date (inclusive).
        date_to: End date (inclusive).
        limit: Maximum number of products to return (default 10).

    Returns:
        List of dicts, each with keys:
        - product_name: Product name
        - color: Variant color
        - size: Variant size
        - sku: Variant SKU
        - quantity: Total quantity sold
        - revenue: Total revenue for this variant

    Example:
        >>> get_top_products(date(2026, 5, 1), date(2026, 5, 7), limit=5)
        [
            {'product_name': 'Air Max 90', 'color': 'Blue', 'size': '42', 'quantity': 15, 'revenue': Decimal('2250.00')},
            ...
        ]
    """
    if limit < 0:
        raise ValueError("limit must be non-negative")

    # Create timezone-aware datetime bounds
    start_dt = timezone.make_aware(datetime.combine(date_from, time.min))
    end_dt = timezone.make_aware(datetime.combine(date_to, time.max))

    items = SalesOrderItem.objects.filter(
        sales_order__sale_date__gte=start_dt,
        sales_order__sale_date__lte=end_dt
    ).select_related('variant', 'variant__product').values(
        'variant__id',
        'variant__product__name',
        'variant__color',
        'variant__size',
        'variant__sku'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('selling_price_at_time') * F('quantity'), output_field=DecimalField())
    ).order_by('-total_quantity')[:limit]

    # Convert to list of dicts with more readable keys
    result = []
    for item in items:
        result.append({
            'product_name': item['variant__product__name'],
            'color': item['variant__color'],
            'size': item['variant__size'],
            'sku': item['variant__sku'],
            'quantity': item['total_quantity'],
            'revenue': item['total_revenue'],
        })

    return result


def get_revenue_data(period: str = 'current_week') -> List[Dict[str, Any]]:
    """
    Get daily revenue and profit for the current week (Monday to Sunday).
    """
    today = timezone.now().date()
    # Find Monday (weekday() returns 0 for Monday)
    monday = today - timedelta(days=today.weekday())

    # Get all 7 days from Monday to Sunday
    week_days = [monday + timedelta(days=i) for i in range(7)]
    start_dt = timezone.make_aware(datetime.combine(week_days[0], time.min))
    end_dt = timezone.make_aware(datetime.combine(week_days[-1], time.max))

    # Query revenue per date
    orders = SalesOrder.objects.filter(
        sale_date__gte=start_dt,
        sale_date__lte=end_dt
    )

    revenue_dict = {}
    for order in orders:
        date_str = str(order.sale_date.date())
        revenue_dict[date_str] = revenue_dict.get(date_str, Decimal('0.00')) + order.total_amount

    # Query profit per date
    items = SalesOrderItem.objects.filter(
        sales_order__sale_date__gte=start_dt,
        sales_order__sale_date__lte=end_dt
    ).select_related('variant')

    profit_dict = {}
    for item in items:
        date_str = str(item.sales_order.sale_date.date())
        profit = (item.selling_price_at_time - item.variant.import_price) * item.quantity
        profit_dict[date_str] = profit_dict.get(date_str, Decimal('0.00')) + profit

    result = []
    for d in week_days:
        date_str = str(d)
        result.append({
            'date': d.strftime('%d-%m'),
            'revenue': revenue_dict.get(date_str, Decimal('0.00')),
            'profit': profit_dict.get(date_str, Decimal('0.00')),
        })

    return result


def get_daily_stats_in_range(date_from: date, date_to: date) -> List[Dict[str, Any]]:
    """
    Get daily revenue and profit for each day in a date range.
    """
    start_dt = timezone.make_aware(datetime.combine(date_from, time.min))
    end_dt = timezone.make_aware(datetime.combine(date_to, time.max))

    # Get revenue data
    orders = SalesOrder.objects.filter(
        sale_date__gte=start_dt,
        sale_date__lte=end_dt
    )
    revenue_dict = {}
    for order in orders:
        d_str = str(order.sale_date.date())
        revenue_dict[d_str] = revenue_dict.get(d_str, Decimal('0.00')) + order.total_amount

    # Get profit data
    items = SalesOrderItem.objects.filter(
        sales_order__sale_date__gte=start_dt,
        sales_order__sale_date__lte=end_dt
    ).select_related('variant')

    profit_dict = {}
    for item in items:
        d_str = str(item.sales_order.sale_date.date())
        profit = (item.selling_price_at_time - item.variant.import_price) * item.quantity
        profit_dict[d_str] = profit_dict.get(d_str, Decimal('0.00')) + profit

    result = []
    delta = (date_to - date_from).days + 1
    for i in range(delta):
        curr_date = date_from + timedelta(days=i)
        d_str = str(curr_date)
        result.append({
            'date': curr_date.strftime('%d-%m'),
            'revenue': float(revenue_dict.get(d_str, Decimal('0.00'))),
            'profit': float(profit_dict.get(d_str, Decimal('0.00'))),
        })
    return result


def get_product_type_distribution(date_from: date, date_to: date) -> List[Dict[str, Any]]:
    """
    Get sold quantities grouped by product type in a date range.
    """
    start_dt = timezone.make_aware(datetime.combine(date_from, time.min))
    end_dt = timezone.make_aware(datetime.combine(date_to, time.max))

    stats = SalesOrderItem.objects.filter(
        sales_order__sale_date__gte=start_dt,
        sales_order__sale_date__lte=end_dt
    ).values(
        'variant__product__type'
    ).annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')

    return [
        {
            'type': item['variant__product__type'] or 'Chưa phân loại',
            'quantity': item['total_quantity']
        } for item in stats
    ]


def get_profit_data(days: int = 30) -> List[Dict[str, Any]]:
    """
    Get daily profit for the last N days (for Chart.js visualization).

    Profit is calculated as: (selling_price_at_time - import_price) * quantity

    Args:
        days: Number of days to include (default 30).

    Returns:
        List of dicts, each with keys:
        - date: Date (YYYY-MM-DD format string)
        - profit: Profit for that day (Decimal)

    Example:
        >>> get_profit_data(7)
        [
            {'date': '2026-05-01', 'profit': Decimal('100000.00')},
            {'date': '2026-05-02', 'profit': Decimal('120000.00')},
            ...
        ]
    """
    if days <= 0:
        raise ValueError("days must be positive")

    start_dt = timezone.make_aware(
        datetime.combine(timezone.now().date() - timedelta(days=days - 1), time.min)
    )
    end_dt = timezone.make_aware(
        datetime.combine(timezone.now().date(), time.max)
    )

    # Query profit per date
    daily_profit = SalesOrderItem.objects.filter(
        sales_order__sale_date__gte=start_dt,
        sales_order__sale_date__lte=end_dt
    ).select_related('variant').annotate(
        sale_date_only=TruncDate('sales_order__sale_date')
    ).values('sale_date_only').annotate(
        daily_profit=Sum(
            (F('selling_price_at_time') - F('variant__import_price')) * F('quantity'),
            output_field=DecimalField()
        )
    ).order_by('sale_date_only')

    result = []
    for entry in daily_profit:
        result.append({
            'date': str(entry['sale_date_only']),
            'profit': entry['daily_profit'] or Decimal('0.00'),
        })

    return result
