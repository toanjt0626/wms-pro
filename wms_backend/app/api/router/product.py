import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product, Lot
from app.schemas.base import ProductCreate, LotCreate

router = APIRouter(prefix="/products", tags=["products"])


@router.post("")
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.sku == payload.sku).first()
    if existing:
        raise HTTPException(409, "SKU đã tồn tại")
    product = Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.post("/lots")
def create_lot(payload: LotCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(
        Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(404, "Sản phẩm không tồn tại")

    expiry = None
    if payload.expiry_date:
        expiry = datetime.date.fromisoformat(payload.expiry_date)

    lot = Lot(product_id=payload.product_id,
              lot_number=payload.lot_number, expiry_date=expiry)
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return lot


@router.get("")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()
