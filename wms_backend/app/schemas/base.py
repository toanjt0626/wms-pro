from typing import Optional, Dict, Any
from pydantic import BaseModel


# ---- Warehouse setup ----
class WarehouseCreate(BaseModel):
    code: str
    name: str


class ZoneCreate(BaseModel):
    warehouse_id: str
    code: str
    name: Optional[str] = None
    velocity_tier: str = "B"
    distance_to_dock: int = 100


class BinCreate(BaseModel):
    zone_id: str
    location_code: str
    qr_code: str
    aisle_index: int = 0
    position_in_aisle: int = 0
    capacity: int = 100


class BinOut(BaseModel):
    id: str
    location_code: str
    qr_code: str
    status: str

    class Config:
        from_attributes = True


# ---- Product ----
class ProductCreate(BaseModel):
    sku: str
    name: str
    industry_type: str = "general"
    custom_attributes: Dict[str, Any] = {}


class LotCreate(BaseModel):
    product_id: str
    lot_number: str
    expiry_date: Optional[str] = None  # ISO format "2026-08-12"


# ---- Inbound ----
class InboundOrderCreate(BaseModel):
    code: str


class InboundOrderItemCreate(BaseModel):
    inbound_order_id: str
    product_id: str
    expected_qty: int


class ConfirmPutawayRequest(BaseModel):
    inbound_order_item_id: str
    lot_id: str
    bin_qr_code: str  # quét QR ô kệ tại chỗ để xác nhận
    quantity: int
    created_by: Optional[str] = None


# ---- Outbound ----
class OutboundOrderCreate(BaseModel):
    code: str
    channel: str = "internal"
    priority: int = 0


class OutboundOrderItemCreate(BaseModel):
    outbound_order_id: str
    product_id: str
    quantity: int


class ConfirmPickRequest(BaseModel):
    outbound_order_item_id: str
    bin_qr_code: str  # quét QR ô kệ xác nhận đúng vị trí
    lot_id: str
    quantity: int
    created_by: Optional[str] = None


# ---- QR scan lookup ----
class BinScanResponse(BaseModel):
    bin_id: str
    location_code: str
    status: str
    # danh sách {product_name, sku, lot_number, expiry_date, quantity}
    items: list
