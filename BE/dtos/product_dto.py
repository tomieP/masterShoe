from dataclasses import dataclass
from typing import List, Optional


@dataclass
class InventoryDTO:
    quantity: int
    min_quantity: int


@dataclass
class VariantDTO:
    id: int
    size: str
    color: str
    price: float
    cost: float
    sku: Optional[str]
    inventory: InventoryDTO


@dataclass
class ProductDTO:
    id: int
    code: str
    name: str
    type: str
    brand: str
    variants: List[VariantDTO]