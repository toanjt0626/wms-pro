from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.orders import OutboundOrder
from app.models.warehouse import Bin
from app.services.routing import PickStop, optimize_picking_route, total_route_distance
from app.services.fefo import assign_lot_fefo
from app.services.batching import batch_orders
from app.schemas.algorithms import PickingRouteResponse, PickStopOut, BatchRequest, BatchResponse

router = APIRouter(prefix="/picking", tags=["picking"])


@router.post("/optimize-route/{outbound_order_id}", response_model=PickingRouteResponse)
def optimize_route(
    outbound_order_id: str,
    layout_complexity: str = "simple",  # "simple" -> S-shape, khác -> nearest neighbor + 2-opt
    db: Session = Depends(get_db),
):
    order = db.query(OutboundOrder).filter(OutboundOrder.id == outbound_order_id).first()
    if not order:
        raise HTTPException(404, "Đơn xuất không tồn tại")

    stops = []
    for item in order.items:
        if item.assigned_bin_id:
            bin_ = db.query(Bin).filter(Bin.id == item.assigned_bin_id).first()
            stops.append(PickStop(order_item_id=item.id, bin=bin_, quantity=item.quantity))
            continue

        allocations, remaining = assign_lot_fefo(db, item.product_id, item.quantity)
        if remaining > 0:
            raise HTTPException(409, f"Không đủ tồn kho cho sản phẩm {item.product_id} (thiếu {remaining})")
        for inv, take in allocations:
            stops.append(PickStop(order_item_id=item.id, bin=inv.bin, quantity=take))

    if not stops:
        raise HTTPException(409, "Đơn xuất chưa có dòng hàng nào")

    ordered = optimize_picking_route(stops, layout_complexity)

    return PickingRouteResponse(
        outbound_order_id=order.id,
        stops=[
            PickStopOut(
                order_item_id=s.order_item_id,
                bin_id=s.bin.id,
                location_code=s.bin.location_code,
                quantity=s.quantity,
                sequence=i + 1,
            )
            for i, s in enumerate(ordered)
        ],
        total_distance=total_route_distance(ordered),
    )


@router.post("/batch", response_model=BatchResponse)
def batch_orders_endpoint(payload: BatchRequest, db: Session = Depends(get_db)):
    """Gộp nhiều đơn nhỏ thành 1 chuyến đi (wave picking) - đặc biệt hữu ích
    cho kho livestream TMĐT khi có hàng trăm đơn nhỏ đổ về cùng lúc."""
    orders = db.query(OutboundOrder).filter(OutboundOrder.id.in_(payload.order_ids)).all()
    if not orders:
        raise HTTPException(404, "Không tìm thấy đơn xuất nào phù hợp")

    batches = batch_orders(orders, payload.cart_capacity)
    return BatchResponse(batches=[[o.id for o in b] for b in batches])
