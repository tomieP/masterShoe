from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Product:
    id: Optional[int] = None
    code: str = ""
    name: str = ""
    type: str = ""
    subtype: Optional[str] = None
    brand: str = ""
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    