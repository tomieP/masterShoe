from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ProductVariant:
    id: Optional[int] = None
    product_id: Optional[int] = None
    color: str = ""
    size: str = ""
    price: float = 0.0
    cost: float = 0.0
    sku: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None