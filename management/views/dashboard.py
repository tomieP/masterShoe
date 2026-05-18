"""
Dashboard and reports views.

This module provides views for displaying sales statistics, revenue data,
and product performance metrics. All views require manager role.

Views:
    - dashboard: Main dashboard with today's stats and charts
    - reports_daily: Daily report with date picker
    - reports_period: Period report with date range picker
    - reports_top_products: Top selling products report
"""
from datetime import date
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.utils import timezone
import json

from management.permissions import manager_required, staff_required
from management.services.inventory_service import get_low_stock_variants
from management.services.reports import (
    get_daily_stats,
    get_period_stats,
    get_top_products,
    get_revenue_data,
    get_profit_data,
)
from management.models import SalesOrder, SalesOrderItem
from django.db.models import Sum, F, DecimalField
from decimal import Decimal
from datetime import datetime, time


@staff_required
def dashboard(request):
    """
    Main dashboard view for manager.

    Displays:
    - Today's statistics (orders, revenue, profit)
    - 7-day revenue chart
    - Top 5 selling products chart
    - Top 10 low-stock items alert table

    Args:
        request: HttpRequest object

    Returns:
        HttpResponse with rendered dashboard template
    """
    today = timezone.now().date()
    is_manager = request.user.groups.filter(name='Manager').exists() or request.user.is_superuser

    # Get today's statistics (both staff and manager can see this)
    daily_stats = get_daily_stats(today)

    context = {
        'today': today,
        'order_count': daily_stats['order_count'],
        'revenue': daily_stats['revenue'],
        'profit': daily_stats['profit'],
        'is_manager': is_manager,
    }

    # Manager-only data
    if is_manager:
        # Get 7-day revenue data (Monday-Sunday of current week)
        revenue_data = get_revenue_data()

        # Get top 5 products for this month
        month_start = today.replace(day=1)
        top_products = get_top_products(month_start, today, limit=5)

        # Get low stock variants (all, then limit to 10 for display)
        low_stock_items = get_low_stock_variants()[:10]

        # Prepare revenue chart data
        revenue_labels = [item['date'] for item in revenue_data]
        revenue_values = [float(item['revenue']) for item in revenue_data]
        profit_values = [float(item['profit']) for item in revenue_data]

        revenue_chart_data = {
            'labels': revenue_labels,
            'datasets': [
                {
                    'label': 'Doanh thu (₫)',
                    'data': revenue_values,
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 2,
                    'fill': True,
                    'tension': 0.4
                },
                {
                    'label': 'Lợi nhuận (₫)',
                    'data': profit_values,
                    'backgroundColor': 'rgba(153, 102, 255, 0.2)',
                    'borderColor': 'rgba(153, 102, 255, 1)',
                    'borderWidth': 2,
                    'fill': True,
                    'tension': 0.4
                }
            ]
        }

        # Prepare top products chart data
        product_labels = [f"{p['product_name']} ({p['size']} {p['color']})" for p in top_products]
        product_quantities = [p['quantity'] for p in top_products]

        top_products_chart_data = {
            'labels': product_labels,
            'datasets': [{
                'label': 'Số lượng bán (cái)',
                'data': product_quantities,
                'backgroundColor': 'rgba(153, 102, 255, 0.2)',
                'borderColor': 'rgba(153, 102, 255, 1)',
                'borderWidth': 1,
            }]
        }

        context.update({
            'revenue_chart_data': json.dumps(revenue_chart_data),
            'top_products_chart_data': json.dumps(top_products_chart_data),
            'low_stock_count': len(low_stock_items),
            'low_stock_items': low_stock_items[:10],  # Top 10 for display
            'top_products': top_products,
        })

    return render(request, 'dashboard/dashboard.html', context)


@manager_required
def reports_period(request):
    """
    Period report view with date range picker.

    Shows sales statistics for a date range.

    Args:
        request: HttpRequest object
            GET parameters:
                date_from (YYYY-MM-DD format, defaults to 30 days ago)
                date_to (YYYY-MM-DD format, defaults to today)

    Returns:
        HttpResponse with rendered period report template
    """
    today = timezone.now().date()
    default_start = today.replace(day=1)  # Start of month

    # Get dates from request
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')

    try:
        date_from = date.fromisoformat(date_from_str) if date_from_str else default_start
        date_to = date.fromisoformat(date_to_str) if date_to_str else today
    except ValueError:
        return HttpResponseBadRequest("Invalid date format. Use YYYY-MM-DD.")

    # Validate date range
    if date_from > date_to:
        date_from, date_to = date_to, date_from

    # Get statistics for the period
    stats = get_period_stats(date_from, date_to)

    # Prepare chart data
    from management.services.reports import get_daily_stats_in_range, get_product_type_distribution

    # 1. Line Chart Data (Daily Revenue & Profit)
    daily_stats = get_daily_stats_in_range(date_from, date_to)
    line_labels = [item['date'] for item in daily_stats]
    line_revenue = [item['revenue'] for item in daily_stats]
    line_profit = [item['profit'] for item in daily_stats]

    line_chart_data = {
        'labels': line_labels,
        'datasets': [
            {
                'label': 'Doanh thu (₫)',
                'data': line_revenue,
                'borderColor': 'rgba(75, 192, 192, 1)',
                'backgroundColor': 'rgba(75, 192, 192, 0.1)',
                'borderWidth': 2,
                'fill': True,
                'tension': 0.4
            },
            {
                'label': 'Lợi nhuận (₫)',
                'data': line_profit,
                'borderColor': 'rgba(153, 102, 255, 1)',
                'backgroundColor': 'rgba(153, 102, 255, 0.1)',
                'borderWidth': 2,
                'fill': True,
                'tension': 0.4
            }
        ]
    }

    # 2. Pie Chart Data (Product Type Distribution)
    type_stats = get_product_type_distribution(date_from, date_to)
    pie_labels = [item['type'] for item in type_stats]
    pie_data = [item['quantity'] for item in type_stats]

    # Dynamic colors for pie chart
    import random
    def get_random_color(opacity=0.6):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return f'rgba({r}, {g}, {b}, {opacity})'

    pie_colors = [get_random_color() for _ in pie_labels]
    pie_border_colors = [c.replace('0.6', '1') for c in pie_colors]

    pie_chart_data = {
        'labels': pie_labels,
        'datasets': [{
            'data': pie_data,
            'backgroundColor': pie_colors,
            'borderColor': pie_border_colors,
            'borderWidth': 1
        }]
    }

    context = {
        'date_from': date_from,
        'date_to': date_to,
        'order_count': stats['order_count'],
        'revenue': stats['revenue'],
        'profit': stats['profit'],
        'line_chart_data': json.dumps(line_chart_data),
        'pie_chart_data': json.dumps(pie_chart_data),
    }

    return render(request, 'dashboard/reports_period.html', context)


@manager_required
def reports_top_products(request):
    """
    Top selling products report view.

    Shows top N selling products in a date range with visualization.

    Args:
        request: HttpRequest object
            GET parameters:
                date_from (YYYY-MM-DD format, defaults to 30 days ago)
                date_to (YYYY-MM-DD format, defaults to today)
                limit (integer, defaults to 10, max 50)

    Returns:
        HttpResponse with rendered top products report template
    """
    today = timezone.now().date()
    default_start = today.replace(day=1)  # Start of month

    # Get dates from request
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')
    limit_str = request.GET.get('limit', '10')

    try:
        date_from = date.fromisoformat(date_from_str) if date_from_str else default_start
        date_to = date.fromisoformat(date_to_str) if date_to_str else today
        limit = int(limit_str)
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Invalid parameters. Check date format (YYYY-MM-DD) and limit (integer).")

    # Validate date range
    if date_from > date_to:
        date_from, date_to = date_to, date_from

    # Limit the limit value (max 50)
    limit = min(max(limit, 1), 50)

    # Get top products
    top_products = get_top_products(date_from, date_to, limit=limit)

    # Prepare chart data
    product_labels = [f"{p['product_name']} ({p['size']} {p['color']})" for p in top_products]
    product_quantities = [p['quantity'] for p in top_products]

    chart_data = {
        'labels': product_labels,
        'datasets': [{
            'label': 'Số lượng bán (cái)',
            'data': product_quantities,
            'backgroundColor': 'rgba(255, 99, 132, 0.2)',
            'borderColor': 'rgba(255, 99, 132, 1)',
            'borderWidth': 1,
        }]
    }

    context = {
        'date_from': date_from,
        'date_to': date_to,
        'limit': limit,
        'top_products': top_products,
        'chart_data': json.dumps(chart_data),
    }

    return render(request, 'dashboard/reports_top_products.html', context)
