from typing import Dict, List
from pydantic import BaseModel


class PutawaySuggestionRequest(BaseModel):
    warehouse_id: str
    product_id: str
    quantity: int


class BinSuggestion(BaseModel):
    bin_id: str
    location_code: str
    qr_code: str
    score: float
    reasons: Dict[str, float]


class PutawaySuggestionResponse(BaseModel):
    suggestions: List[BinSuggestion]


class PickStopOut(BaseModel):
    order_item_id: str
    bin_id: str
    location_code: str
    quantity: int
    sequence: int


class PickingRouteResponse(BaseModel):
    outbound_order_id: str
    stops: List[PickStopOut]
    total_distance: float


class BatchRequest(BaseModel):
    order_ids: List[str]
    cart_capacity: int = 50


class BatchResponse(BaseModel):
    batches: List[List[str]]
