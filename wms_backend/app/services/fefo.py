"""
Phân bổ lô hàng khi xuất kho theo FEFO (First Expired First Out) hoặc FIFO.

Với sản phẩm có expiry_date (FMCG), ưu tiên lô hết hạn sớm nhất trước.
Với sản phẩm không theo dõi hạn dùng, expiry_date NULL sẽ tự động xếp cuối,
tương đương hành vi FIFO theo thứ tự tạo lô.
"""
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Lot


def assign_lot_fefo(db: Session, product_id: str, quantity_needed: int) -> Tuple[List[Tuple[Inventory, int]], int]:
    """Trả về danh sách (bản ghi tồn kho, số lượng lấy từ đó) và số lượng
    còn thiếu (0 nếu đủ hàng)."""
    inventories = (
        db.query(Inventory)
        .join(Lot, Inventory.lot_id == Lot.id)
        .filter(Lot.product_id == product_id, Inventory.quantity > 0)
        .order_by(Lot.expiry_date.is_(None), Lot.expiry_date.asc())
        .all()
    )

    allocations: List[Tuple[Inventory, int]] = []
    remaining = quantity_needed
    for inv in inventories:
        if remaining <= 0:
            break
        take = min(inv.quantity, remaining)
        allocations.append((inv, take))
        remaining -= take

    return allocations, remaining
