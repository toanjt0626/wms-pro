"""
Chạy: python seed.py
Tạo sẵn 1 kho, 2 khu vực (golden zone gần cửa xuất + zone thường),
mỗi khu vực vài dãy kệ với nhiều ô, và 2 sản phẩm mẫu (1 FMCG có hạn dùng,
1 hàng thường) để bạn test luôn API mà không cần tạo tay từng bước.
"""
import datetime

from app.database import Base, engine, SessionLocal
from app.models.warehouse import Warehouse, Zone, Bin
from app.models.product import Product, Lot

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# --- Kho + khu vực ---
wh = Warehouse(code="KHO-A", name="Kho A - Trung tâm")
db.add(wh)
db.commit()
db.refresh(wh)

zone_golden = Zone(warehouse_id=wh.id, code="Z1", name="Khu vực gần cửa xuất (golden zone)",
                   velocity_tier="A", distance_to_dock=20)
zone_normal = Zone(warehouse_id=wh.id, code="Z2", name="Khu vực thường",
                   velocity_tier="C", distance_to_dock=300)
db.add_all([zone_golden, zone_normal])
db.commit()
db.refresh(zone_golden)
db.refresh(zone_normal)

# --- Ô kệ: 2 dãy trong mỗi khu vực, mỗi dãy 5 ô ---
bins = []
for zone, prefix, aisle_start in [(zone_golden, "A1", 1), (zone_normal, "B1", 3)]:
    for aisle in range(aisle_start, aisle_start + 2):
        for pos in range(1, 6):
            code = f"{prefix}-{aisle:02d}-{pos:02d}"
            bins.append(
                Bin(
                    zone_id=zone.id,
                    location_code=code,
                    qr_code=f"QR-{code}",
                    aisle_index=aisle,
                    position_in_aisle=pos,
                    capacity=100,
                )
            )
db.add_all(bins)
db.commit()

# --- Sản phẩm mẫu ---
milk = Product(sku="SUA-TUOI-1L", name="Sữa tươi 1L", industry_type="fmcg",
               custom_attributes={"shelf_life_days": 30}, velocity_tier="A")
shirt = Product(sku="AO-THUN-DEN-L", name="Áo thun đen size L", industry_type="garment",
                custom_attributes={"size": "L", "color": "đen"}, velocity_tier="B")
db.add_all([milk, shirt])
db.commit()
db.refresh(milk)
db.refresh(shirt)

lot_milk = Lot(product_id=milk.id, lot_number="LOT-2607",
               expiry_date=datetime.date.today() + datetime.timedelta(days=21))
lot_shirt = Lot(product_id=shirt.id,
                lot_number="LOT-SHIRT-01", expiry_date=None)
db.add_all([lot_milk, lot_shirt])
db.commit()

print("Seed xong.")
print(f"warehouse_id = {wh.id}")
print(f"product milk id = {milk.id}, lot_milk id = {lot_milk.id}")
print(f"product shirt id = {shirt.id}, lot_shirt id = {lot_shirt.id}")
print("Mẫu QR ô kệ đã tạo: QR-A1-01-01 ... QR-B1-04-05 (tổng 20 ô)")

db.close()
