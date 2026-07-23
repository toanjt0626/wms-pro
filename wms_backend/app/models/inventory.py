import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.warehouse import gen_uuid


class Inventory(Base):
    """Tồn kho hiện tại tại từng ô kệ, theo từng lô. Đây là bảng 'snapshot',
    luôn được cập nhật dựa trên InventoryTransaction - không sửa tay trực tiếp."""
    __tablename__ = "inventory"

    id = Column(String, primary_key=True, default=gen_uuid)
    bin_id = Column(String, ForeignKey("bins.id"), nullable=False)
    lot_id = Column(String, ForeignKey("lots.id"), nullable=False)
    quantity = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    bin = relationship("Bin")
    lot = relationship("Lot")


class InventoryTransaction(Base):
    """Sổ cái (ledger) - ghi lại MỌI thay đổi tồn kho, không bao giờ xoá/sửa.
    Đây là nguồn dữ liệu để truy vết, đối chiếu, và tính lại ABC velocity."""
    __tablename__ = "inventory_transactions"

    id = Column(String, primary_key=True, default=gen_uuid)
    bin_id = Column(String, ForeignKey("bins.id"), nullable=False)
    lot_id = Column(String, ForeignKey("lots.id"), nullable=False)

    type = Column(String, nullable=False)  # IN / OUT / TRANSFER / ADJUST
    quantity_change = Column(Integer, nullable=False)  # dương cho IN, âm cho OUT

    ref_type = Column(String, nullable=True)  # vd: inbound_order / outbound_order
    ref_id = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
