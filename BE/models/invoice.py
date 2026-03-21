from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Invoice:
    id: Optional[int] = None
    code: str = ""
    user_id: int = ""
    payment_method: str = ""
    payment_status: str = "finished"
    note: Optional[str] = None
    total: Optional[float] = 0.00
    created_at: Optional[datetime] = None
