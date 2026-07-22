from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings


# Import models để SQLAlchemy biết và tạo bảng
from app.models import warehouse, product, inventory, orders  # noqa: F401

from app.api.router import (
    routes_warehouse,
    routes_product,
    routes_inbound,
    routes_outbound,
    routes_slotting,
    routes_picking,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Backend quản lý kho: nhập/xuất kho, gợi ý vị trí lưu trữ (slotting), "
    "định tuyến pick hàng (S-shape / TSP), gộp đơn (batch picking).",
    version="0.1.0",
)

# Cho phép frontend Vite (chạy ở localhost:5173 khi dev) gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # production nên giới hạn lại domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_warehouse)
app.include_router(routes_product)
app.include_router(routes_inbound)
app.include_router(routes_outbound)
app.include_router(routes_slotting)
app.include_router(routes_picking)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}
