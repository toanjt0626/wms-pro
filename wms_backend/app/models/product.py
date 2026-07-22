from sqlalchemy import Column, String, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.warehouse import gen_uuid


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=gen_uuid)
    sku = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)

    # Loại ngành hàng - quyết định bộ trọng số thuật toán slotting và quy tắc FEFO/FIFO
    # Giá trị hợp lệ: general | fmcg | electronics | garment | printing | livestream
    industry_type = Column(String, default="general")

    # Thuộc tính riêng theo ngành, không cần sửa schema khi thêm ngành mới
    # vd FMCG: {"shelf_life_days": 180}; garment: {"size": "L", "color": "đen"}
    custom_attributes = Column(JSON, default=dict)

    # Xếp hạng tốc độ luân chuyển A/B/C, được job định kỳ tính lại (xem services/slotting.py)
    velocity_tier = Column(String, default="B")

    lots = relationship("Lot", back_populates="product")


class Lot(Base):
    __tablename__ = "lots"

    id = Column(String, primary_key=True, default=gen_uuid)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    lot_number = Column(String, nullable=False)
    # null nếu ngành hàng không cần theo dõi hạn dùng
    expiry_date = Column(Date, nullable=True)

    product = relationship("Product", back_populates="lots")
