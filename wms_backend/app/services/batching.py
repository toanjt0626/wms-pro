"""
Thuật toán gộp đơn (batch/wave picking) - dùng thuật toán "seed": chọn 1 đơn
làm hạt giống, sau đó lần lượt thêm các đơn khác vào cùng chuyến nếu vị trí
lấy hàng có dãy kệ trùng nhau và còn đủ sức chứa xe đẩy.

Đặc biệt quan trọng cho kho livestream TMĐT - nơi hàng trăm đơn nhỏ đổ về
cùng lúc, pick từng đơn một sẽ rất lãng phí quãng đường di chuyển.
"""
from typing import List

from app.models.orders import OutboundOrder


def _order_quantity(order: OutboundOrder) -> int:
    return sum(item.quantity for item in order.items)


def _order_aisles(order: OutboundOrder) -> set:
    return {
        item.assigned_bin.aisle_index
        for item in order.items
        if item.assigned_bin is not None
    }


def batch_orders(orders: List[OutboundOrder], cart_capacity: int) -> List[List[OutboundOrder]]:
    unassigned = list(orders)
    batches: List[List[OutboundOrder]] = []

    while unassigned:
        seed = unassigned.pop(0)
        batch = [seed]
        capacity_used = _order_quantity(seed)
        aisles_in_batch = _order_aisles(seed)

        remaining = []
        for other in unassigned:
            other_qty = _order_quantity(other)
            other_aisles = _order_aisles(other)
            overlaps = len(aisles_in_batch & other_aisles) > 0

            if capacity_used + other_qty <= cart_capacity and overlaps:
                batch.append(other)
                capacity_used += other_qty
                aisles_in_batch |= other_aisles
            else:
                remaining.append(other)

        unassigned = remaining
        batches.append(batch)

    return batches
