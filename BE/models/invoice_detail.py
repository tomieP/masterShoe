from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class InvoiceDetail:
    id: Optional[int] = None
    invoice_id: Optional[int] = None
    variant_id: Optional[int] = None
    quantity: int = 0
    price: float = 0.0

