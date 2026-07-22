import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.orders import InboundOrder, InboundOrderItem
from app.models.warehouse import Bin
from app.models.product import Lot
from app.models.inventory import Inventory, InventoryTransaction
from app.schemas.base import InboundOrderCreate, InboundOrderItemCreate, ConfirmPutawayRequest

router = APIRouter(prefix="/inbound", tags=["inbound"])


@router.post("/orders")
def create_inbound_order(payload: InboundOrderCreate, db: Session = Depends(get_db)):
    order = InboundOrder(code=payload.code, status="draft")
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.post("/orders/items")
def add_inbound_item(payload: InboundOrderItemCreate, db: Session = Depends(get_db)):
    order = db.query(InboundOrder).filter(
        InboundOrder.id == payload.inbound_order_id).first()
    if not order:
        raise HTTPException(404, "Phiếu nhập không tồn tại")
    item = InboundOrderItem(**payload.dict())
    db.add(item)
    order.status = "confirmed"
    db.commit()
    db.refresh(item)
    return item


@router.post("/confirm-putaway")
def confirm_putaway(payload: ConfirmPutawayRequest, db: Session = Depends(get_db)):
    """Nhân viên quét QR ô kệ tại chỗ để xác nhận cất hàng - đây là bước
    chốt sau khi đã nhận gợi ý vị trí từ /slotting/suggest."""
    item = db.query(InboundOrderItem).filter(
        InboundOrderItem.id == payload.inbound_order_item_id).first()
    if not item:
        raise HTTPException(404, "Dòng phiếu nhập không tồn tại")

    bin_ = db.query(Bin).filter(Bin.qr_code == payload.bin_qr_code).first()
    if not bin_ or bin_.status != "active":
        raise HTTPException(404, "Mã QR ô kệ không hợp lệ hoặc ô đang bị khoá")

    lot = db.query(Lot).filter(Lot.id == payload.lot_id).first()
    if not lot:
        raise HTTPException(404, "Lô hàng không tồn tại")

    inv = (
        db.query(Inventory)
        .filter(Inventory.bin_id == bin_.id, Inventory.lot_id == lot.id)
        .first()
    )
    if inv:
        inv.quantity += payload.quantity
        inv.updated_at = datetime.datetime.utcnow()
    else:
        inv = Inventory(bin_id=bin_.id, lot_id=lot.id,
                        quantity=payload.quantity)
        db.add(inv)

    db.add(
        InventoryTransaction(
            bin_id=bin_.id,
            lot_id=lot.id,
            type="IN",
            quantity_change=payload.quantity,
            ref_type="inbound_order_item",
            ref_id=item.id,
            created_by=payload.created_by,
        )
    )

    item.received_qty += payload.quantity
    if item.received_qty >= item.expected_qty:
        item.order.status = "completed"
    else:
        item.order.status = "receiving"

    db.commit()
    return {
        "status": "ok",
        "bin_location_code": bin_.location_code,
        "received_qty": item.received_qty,
        "expected_qty": item.expected_qty,
    }
