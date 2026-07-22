import uuid

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(String, primary_key=True, default=gen_uuid)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)

    zones = relationship("Zone", back_populates="warehouse")


class Zone(Base):
    __tablename__ = "zones"

    id = Column(String, primary_key=True, default=gen_uuid)
    warehouse_id = Column(String, ForeignKey("warehouses.id"), nullable=False)
    code = Column(String, nullable=False)
    name = Column(String)

    # Dùng cho thuật toán slotting: A/B/C tương ứng hàng bán chạy/trung bình/chậm
    velocity_tier = Column(String, default="B")
    # Khoảng cách quy đổi (mét) từ khu vực này tới cửa nhận/xuất hàng, tính sẵn khi setup kho
    distance_to_dock = Column(Integer, default=100)

    warehouse = relationship("Warehouse", back_populates="zones")
    bins = relationship("Bin", back_populates="zone")


class Bin(Base):
    __tablename__ = "bins"

    id = Column(String, primary_key=True, default=gen_uuid)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=False)

    location_code = Column(String, unique=True, nullable=False)  # vd: A1-02-03
    # mã QR dán vật lý trên ô kệ
    qr_code = Column(String, unique=True, nullable=False)

    # Toạ độ logic dùng cho thuật toán định tuyến pick hàng (S-shape / TSP)
    aisle_index = Column(Integer, default=0)
    position_in_aisle = Column(Integer, default=0)

    # sức chứa quy đổi (đơn vị chung, vd: số thùng)
    capacity = Column(Integer, default=100)
    status = Column(String, default="active")  # active / blocked / maintenance

    zone = relationship("Zone", back_populates="bins")
