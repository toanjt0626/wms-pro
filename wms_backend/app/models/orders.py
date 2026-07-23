import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.warehouse import gen_uuid


class InboundOrder(Base):
    __tablename__ = "inbound_orders"

    id = Column(String, primary_key=True, default=gen_uuid)
    code = Column(String, unique=True, nullable=False)
    status = Column(String, default="draft")  # draft -> confirmed -> receiving -> completed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    items = relationship("InboundOrderItem", back_populates="order")


class InboundOrderItem(Base):
    __tablename__ = "inbound_order_items"

    id = Column(String, primary_key=True, default=gen_uuid)
    inbound_order_id = Column(String, ForeignKey("inbound_orders.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    expected_qty = Column(Integer, default=0)
    received_qty = Column(Integer, default=0)

    order = relationship("InboundOrder", back_populates="items")


class OutboundOrder(Base):
    __tablename__ = "outbound_orders"

    id = Column(String, primary_key=True, default=gen_uuid)
    code = Column(String, unique=True, nullable=False)
    channel = Column(String, default="internal")  # internal / shopee / tiktok_shop / lazada
    status = Column(String, default="pending")  # pending -> picking -> packed -> shipped
    priority = Column(Integer, default=0)  # cao hơn = ưu tiên hơn (đơn flash-sale livestream)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    items = relationship("OutboundOrderItem", back_populates="order")


class OutboundOrderItem(Base):
    __tablename__ = "outbound_order_items"

    id = Column(String, primary_key=True, default=gen_uuid)
    outbound_order_id = Column(String, ForeignKey("outbound_orders.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=0)

    # Được gán khi hệ thống tính FEFO/FIFO, hoặc khi thủ kho xác nhận thủ công
    assigned_bin_id = Column(String, ForeignKey("bins.id"), nullable=True)
    assigned_lot_id = Column(String, ForeignKey("lots.id"), nullable=True)

    order = relationship("OutboundOrder", back_populates="items")
