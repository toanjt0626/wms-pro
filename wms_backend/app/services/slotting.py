"""
Thuật toán gợi ý vị trí lưu trữ (Putaway Slotting).

Quy trình: lọc cứng (hard filter) loại bỏ ô không hợp lệ -> chấm điểm các ô
còn lại theo 4 tiêu chí có trọng số (ABC velocity, gom nhóm, sức chứa,
khoảng cách) -> xếp hạng, trả về top N gợi ý.

Trọng số được cấu hình riêng theo industry_type - đây chính là cách một hệ
thống dùng chung phục vụ được nhiều ngành hàng khác nhau mà không cần sửa code.
"""
from dataclasses import dataclass, field
from typing import Dict, List

from sqlalchemy.orm import Session

from app.models.inventory import Inventory, InventoryTransaction
from app.models.product import Product, Lot
from app.models.warehouse import Bin, Zone

DEFAULT_WEIGHTS = {"abc": 0.3, "consolidate": 0.3, "capacity": 0.2, "distance": 0.2}

# Trọng số theo ngành - xem giải thích ở phần thiết kế thuật toán slotting.
INDUSTRY_WEIGHTS: Dict[str, Dict[str, float]] = {
    "livestream": {"abc": 0.25, "consolidate": 0.15, "capacity": 0.10, "distance": 0.50},
    "fmcg": {"abc": 0.25, "consolidate": 0.45, "capacity": 0.15, "distance": 0.15},
    "electronics": {"abc": 0.30, "consolidate": 0.20, "capacity": 0.30, "distance": 0.20},
    "garment": {"abc": 0.20, "consolidate": 0.40, "capacity": 0.20, "distance": 0.20},
    "printing": {"abc": 0.10, "consolidate": 0.50, "capacity": 0.20, "distance": 0.20},
    "general": DEFAULT_WEIGHTS,
}

VELOCITY_TIER_ORDER = {"A": 0, "B": 1, "C": 2}


@dataclass
class BinCandidate:
    bin: Bin
    score: float
    reasons: Dict[str, float] = field(default_factory=dict)


def _bin_used_capacity(db: Session, bin_id: str) -> int:
    rows = db.query(Inventory).filter(Inventory.bin_id == bin_id).all()
    return sum(r.quantity for r in rows)


def hard_filter_bins(db: Session, warehouse_id: str, quantity: int) -> List[Bin]:
    """Loại bỏ ngay các ô không đủ điều kiện, không cần chấm điểm."""
    zone_ids = [z.id for z in db.query(Zone).filter(Zone.warehouse_id == warehouse_id).all()]
    if not zone_ids:
        return []

    candidates = (
        db.query(Bin)
        .filter(Bin.zone_id.in_(zone_ids))
        .filter(Bin.status == "active")
        .all()
    )
    return [b for b in candidates if (b.capacity - _bin_used_capacity(db, b.id)) >= quantity]


def abc_zone_match_score(bin_: Bin, product: Product) -> float:
    """Điểm cao nếu hạng tốc độ luân chuyển của sản phẩm (A/B/C) khớp với
    hạng của khu vực (golden zone gần cửa xuất dành cho hàng A)."""
    p_rank = VELOCITY_TIER_ORDER.get(product.velocity_tier, 1)
    z_rank = VELOCITY_TIER_ORDER.get(bin_.zone.velocity_tier, 1)
    diff = abs(p_rank - z_rank)
    if diff == 0:
        return 1.0
    if diff == 1:
        return 0.5
    return 0.0


def consolidation_score(db: Session, bin_: Bin, product_id: str) -> float:
    """Ưu tiên ô đã có sẵn cùng SKU (giảm phân mảnh hàng rải rác khắp kho)."""
    existing = (
        db.query(Inventory)
        .join(Lot, Inventory.lot_id == Lot.id)
        .filter(Inventory.bin_id == bin_.id, Lot.product_id == product_id)
        .first()
    )
    if existing:
        return 1.0
    used = _bin_used_capacity(db, bin_.id)
    return 0.5 if used == 0 else 0.1


def capacity_fit_score(db: Session, bin_: Bin, quantity: int) -> float:
    """Ưu tiên ô có sức chứa gần khớp với số lượng cần xếp, tránh lãng phí
    một ô lớn cho một lượng hàng nhỏ."""
    if bin_.capacity == 0:
        return 0.0
    used = _bin_used_capacity(db, bin_.id)
    free = bin_.capacity - used
    fit = 1 - abs(free - quantity) / bin_.capacity
    return max(0.0, fit)


def distance_score(bin_: Bin, max_distance: int = 500) -> float:
    """Ô càng gần cửa nhận/xuất hàng càng được điểm cao."""
    d = bin_.zone.distance_to_dock or 0
    return max(0.0, 1 - d / max_distance)


def suggest_putaway(
    db: Session, warehouse_id: str, product: Product, quantity: int, top_n: int = 3
) -> List[BinCandidate]:
    weights = INDUSTRY_WEIGHTS.get(product.industry_type, DEFAULT_WEIGHTS)
    candidates = hard_filter_bins(db, warehouse_id, quantity)

    scored: List[BinCandidate] = []
    for b in candidates:
        s_abc = abc_zone_match_score(b, product)
        s_cons = consolidation_score(db, b, product.id)
        s_cap = capacity_fit_score(db, b, quantity)
        s_dist = distance_score(b)
        total = (
            weights["abc"] * s_abc
            + weights["consolidate"] * s_cons
            + weights["capacity"] * s_cap
            + weights["distance"] * s_dist
        )
        scored.append(
            BinCandidate(
                bin=b,
                score=round(total, 4),
                reasons={"abc": s_abc, "consolidate": s_cons, "capacity": s_cap, "distance": s_dist},
            )
        )

    scored.sort(key=lambda c: -c.score)
    return scored[:top_n]


def recompute_velocity_tiers(db: Session, warehouse_id: str, lookback_days: int = 90) -> None:
    """Job định kỳ: tính lại hạng A/B/C cho từng sản phẩm dựa trên số lượt
    xuất kho gần đây (nguyên lý Pareto: top 20% = A, tiếp 30% = B, còn lại = C).
    Nên chạy hàng tuần với kho thường, hàng ngày với kho livestream."""
    import datetime

    since = datetime.datetime.utcnow() - datetime.timedelta(days=lookback_days)

    tx = (
        db.query(InventoryTransaction, Lot.product_id)
        .join(Lot, InventoryTransaction.lot_id == Lot.id)
        .filter(InventoryTransaction.type == "OUT", InventoryTransaction.created_at >= since)
        .all()
    )

    pick_counts: Dict[str, int] = {}
    for _, product_id in tx:
        pick_counts[product_id] = pick_counts.get(product_id, 0) + 1

    if not pick_counts:
        return

    ranked = sorted(pick_counts.items(), key=lambda kv: -kv[1])
    n = len(ranked)
    a_cutoff = max(1, int(n * 0.2))
    b_cutoff = max(a_cutoff + 1, int(n * 0.5))

    for idx, (product_id, _count) in enumerate(ranked):
        tier = "A" if idx < a_cutoff else ("B" if idx < b_cutoff else "C")
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            product.velocity_tier = tier
    db.commit()
