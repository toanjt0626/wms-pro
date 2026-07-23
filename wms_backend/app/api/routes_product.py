import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product, Lot
from app.schemas.base import ProductCreate, LotCreate

router = APIRouter(prefix="/products", tags=["products"])


def _product_dict(p: Product) -> dict:
    return {
        "id": p.id,
        "sku": p.sku,
        "name": p.name,
        "industry_type": p.industry_type,
        "velocity_tier": p.velocity_tier,
        "custom_attributes": p.custom_attributes,
    }


def _lot_dict(l: Lot) -> dict:
    return {
        "id": l.id,
        "product_id": l.product_id,
        "lot_number": l.lot_number,
        "expiry_date": l.expiry_date.isoformat() if l.expiry_date else None,
    }


@router.post("")
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.sku == payload.sku).first()
    if existing:
        raise HTTPException(409, "SKU đã tồn tại")
    product = Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return _product_dict(product)


@router.get("")
def list_products(db: Session = Depends(get_db)):
    return [_product_dict(p) for p in db.query(Product).all()]


@router.post("/lots")
def create_lot(payload: LotCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(404, "Sản phẩm không tồn tại")

    expiry = None
    if payload.expiry_date:
        expiry = datetime.date.fromisoformat(payload.expiry_date)

    lot = Lot(product_id=payload.product_id, lot_number=payload.lot_number, expiry_date=expiry)
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return _lot_dict(lot)


@router.get("/{product_id}/lots")
def list_product_lots(product_id: str, db: Session = Depends(get_db)):
    lots = db.query(Lot).filter(Lot.product_id == product_id).all()
    return [_lot_dict(l) for l in lots]
