from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.services.slotting import suggest_putaway, recompute_velocity_tiers
from app.schemas.algorithms import PutawaySuggestionRequest, PutawaySuggestionResponse, BinSuggestion

router = APIRouter(prefix="/slotting", tags=["slotting"])


@router.post("/suggest", response_model=PutawaySuggestionResponse)
def suggest_bin(req: PutawaySuggestionRequest, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == req.product_id).first()
    if not product:
        raise HTTPException(404, "Sản phẩm không tồn tại")

    candidates = suggest_putaway(db, req.warehouse_id, product, req.quantity)
    if not candidates:
        raise HTTPException(409, "Không tìm thấy ô kệ nào đủ điều kiện - kiểm tra lại sức chứa hoặc mở thêm khu vực")

    return PutawaySuggestionResponse(
        suggestions=[
            BinSuggestion(
                bin_id=c.bin.id,
                location_code=c.bin.location_code,
                qr_code=c.bin.qr_code,
                score=c.score,
                reasons=c.reasons,
            )
            for c in candidates
        ]
    )


@router.post("/recompute-velocity/{warehouse_id}")
def recompute_velocity(warehouse_id: str, lookback_days: int = 90, db: Session = Depends(get_db)):
    """Chạy định kỳ (cron job hàng tuần, hoặc hàng ngày với kho livestream)
    để tính lại hạng A/B/C cho từng sản phẩm dựa trên tần suất xuất kho gần đây."""
    recompute_velocity_tiers(db, warehouse_id, lookback_days)
    return {"status": "ok", "message": "Đã tính lại velocity tier cho các sản phẩm"}
