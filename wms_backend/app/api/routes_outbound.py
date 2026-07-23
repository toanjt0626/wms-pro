from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.orders import OutboundOrder, OutboundOrderItem
from app.models.warehouse import Bin
from app.models.product import Lot
from app.models.inventory import Inventory, InventoryTransaction
from app.schemas.base import OutboundOrderCreate, OutboundOrderItemCreate, ConfirmPickRequest

router = APIRouter(prefix="/outbound", tags=["outbound"])


@router.post("/orders")
def create_outbound_order(payload: OutboundOrderCreate, db: Session = Depends(get_db)):
    order = OutboundOrder(code=payload.code, channel=payload.channel, priority=payload.priority)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.post("/orders/items")
def add_outbound_item(payload: OutboundOrderItemCreate, db: Session = Depends(get_db)):
    order = db.query(OutboundOrder).filter(OutboundOrder.id == payload.outbound_order_id).first()
    if not order:
        raise HTTPException(404, "Phiếu xuất không tồn tại")
    item = OutboundOrderItem(**payload.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/confirm-pick")
def confirm_pick(payload: ConfirmPickRequest, db: Session = Depends(get_db)):
    """Bước quét kép: quét QR ô kệ để xác nhận đúng vị trí, sau đó xác nhận
    đúng lô hàng - giúp tránh xuất nhầm SKU hoặc nhầm lô (quan trọng với FEFO)."""
    item = db.query(OutboundOrderItem).filter(OutboundOrderItem.id == payload.outbound_order_item_id).first()
    if not item:
        raise HTTPException(404, "Dòng phiếu xuất không tồn tại")

    bin_ = db.query(Bin).filter(Bin.qr_code == payload.bin_qr_code).first()
    if not bin_:
        raise HTTPException(404, "Mã QR ô kệ không hợp lệ")

    lot = db.query(Lot).filter(Lot.id == payload.lot_id).first()
    if not lot:
        raise HTTPException(404, "Lô hàng không tồn tại")

    inv = db.query(Inventory).filter(Inventory.bin_id == bin_.id, Inventory.lot_id == lot.id).first()
    if not inv or inv.quantity < payload.quantity:
        raise HTTPException(409, "Tồn kho thực tế tại vị trí này không đủ - có thể có lệch số liệu, cần tạo phiếu điều chỉnh")

    inv.quantity -= payload.quantity

    db.add(
        InventoryTransaction(
            bin_id=bin_.id,
            lot_id=lot.id,
            type="OUT",
            quantity_change=-payload.quantity,
            ref_type="outbound_order_item",
            ref_id=item.id,
            created_by=payload.created_by,
        )
    )

    item.assigned_bin_id = bin_.id
    item.assigned_lot_id = lot.id

    all_items = item.order.items
    if all(i.assigned_bin_id is not None for i in all_items):
        item.order.status = "packed"
    else:
        item.order.status = "picking"

    db.commit()
    return {"status": "ok", "remaining_in_bin": inv.quantity}
