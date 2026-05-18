from django import template

register = template.Library()

@register.filter
def calculate_profit(sale_order_item):
    """
    Calculates profit for a specific sales order item.
    Profit = (selling_price_at_time - import_price) * quantity
    """
    import_price = sale_order_item.variant.import_price
    selling_price = sale_order_item.selling_price_at_time
    qty = sale_order_item.quantity

    return (selling_price - import_price) * qty