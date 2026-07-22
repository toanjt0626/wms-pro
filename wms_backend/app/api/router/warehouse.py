from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.warehouse import Warehouse, Zone, Bin
from app.models.inventory import Inventory
from app.schemas.base import WarehouseCreate, ZoneCreate, BinCreate, BinOut, BinScanResponse

router = APIRouter(prefix="/warehouse", tags=["warehouse-setup"])


@router.post("/warehouses")
def create_warehouse(payload: WarehouseCreate, db: Session = Depends(get_db)):
    wh = Warehouse(code=payload.code, name=payload.name)
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return wh


@router.post("/zones")
def create_zone(payload: ZoneCreate, db: Session = Depends(get_db)):
    wh = db.query(Warehouse).filter(
        Warehouse.id == payload.warehouse_id).first()
    if not wh:
        raise HTTPException(404, "Kho không tồn tại")
    zone = Zone(**payload.dict())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router.post("/bins", response_model=BinOut)
def create_bin(payload: BinCreate, db: Session = Depends(get_db)):
    zone = db.query(Zone).filter(Zone.id == payload.zone_id).first()
    if not zone:
        raise HTTPException(404, "Khu vực không tồn tại")
    existing = db.query(Bin).filter(Bin.qr_code == payload.qr_code).first()
    if existing:
        raise HTTPException(409, "Mã QR này đã được sử dụng cho ô kệ khác")
    bin_ = Bin(**payload.dict())
    db.add(bin_)
    db.commit()
    db.refresh(bin_)
    return bin_


@router.get("/bins/scan/{qr_code}", response_model=BinScanResponse)
def scan_bin(qr_code: str, db: Session = Depends(get_db)):
    """Đây là endpoint chính khi nhân viên/giám đốc quét QR trên ô kệ bằng
    điện thoại - trả về ngay tình trạng lô hàng hiện tại tại vị trí đó."""
    bin_ = db.query(Bin).filter(Bin.qr_code == qr_code).first()
    if not bin_:
        raise HTTPException(404, "Không tìm thấy ô kệ với mã QR này")

    inventories = db.query(Inventory).filter(
        Inventory.bin_id == bin_.id, Inventory.quantity > 0).all()
    items = []
    for inv in inventories:
        lot = inv.lot
        product = lot.product if lot else None
        items.append(
            {
                "product_name": product.name if product else None,
                "sku": product.sku if product else None,
                "lot_number": lot.lot_number if lot else None,
                "expiry_date": lot.expiry_date.isoformat() if lot and lot.expiry_date else None,
                "quantity": inv.quantity,
            }
        )

    return BinScanResponse(
        bin_id=bin_.id, location_code=bin_.location_code, status=bin_.status, items=items
    )
