from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Inventory:
    id: Optional[int] = None
    variant_id: Optional[int] = None
    quantity: int = 0
    min_quantity: int = 5
    updated_at: Optional[datetime] = None
