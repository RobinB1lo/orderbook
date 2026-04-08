from pydantic import BaseModel
from .models import Side, Type


class OrderRequest(BaseModel):
    symbol: str
    side: Side
    type: Type
    price: float
    quantity: int
