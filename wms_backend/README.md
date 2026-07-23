# WMS Backend

Backend quản lý kho bằng FastAPI, hiện thực các thuật toán đã thiết kế:
- **Slotting**: gợi ý vị trí lưu trữ khi nhập kho (chấm điểm đa tiêu chí, cấu hình theo ngành)
- **Picking route**: định tuyến pick hàng (S-shape cho kho đơn giản, nearest neighbor + 2-opt cho kho phức tạp)
- **Batch picking**: gộp nhiều đơn nhỏ thành 1 chuyến (thuật toán seed) — dành cho kho livestream TMĐT
- **FEFO/FIFO**: tự động phân bổ lô hàng khi xuất kho
- QR code trên từng ô kệ: tra cứu tức thời tình trạng hàng hoá

## Cài đặt

```bash
cd wms_backend
pip install -r requirements.txt

# Tạo dữ liệu mẫu (1 kho, 2 khu vực, 20 ô kệ, 2 sản phẩm) để test nhanh
python seed.py

# Chạy server
uvicorn app.main:app --reload --port 8000
```

Mặc định dùng SQLite (file `wms.db`) để chạy ngay không cần cài gì thêm.
Khi lên production, đổi sang PostgreSQL bằng biến môi trường:

```bash
export DATABASE_URL="postgresql://user:password@host:5432/wms"
```

Xem toàn bộ API và thử trực tiếp tại: **http://127.0.0.1:8000/docs** (Swagger UI tự sinh bởi FastAPI).

## Cấu trúc thư mục

```
app/
  models/        # SQLAlchemy models (đúng theo ERD đã thiết kế)
  schemas/       # Pydantic request/response
  services/      # Thuật toán thuần Python, không phụ thuộc FastAPI
    slotting.py    - gợi ý vị trí lưu trữ + tính lại velocity tier A/B/C
    routing.py     - S-shape, nearest neighbor + 2-opt
    batching.py    - gộp đơn (seed algorithm)
    fefo.py        - phân bổ lô theo FEFO/FIFO
  api/           # FastAPI routers, chỉ gọi xuống services/
  main.py        # khởi tạo app, gắn router, tạo bảng DB
seed.py          # dữ liệu mẫu để test
```

Tách `services/` riêng khỏi `api/` để có thể viết unit test cho thuật toán mà không cần chạy cả server hay chạm vào DB thật.

## Luồng nghiệp vụ chính (test bằng curl hoặc /docs)

1. **Setup kho**: `POST /warehouse/warehouses` → `POST /warehouse/zones` → `POST /warehouse/bins`
2. **Setup sản phẩm**: `POST /products` → `POST /products/lots`
3. **Nhập kho**:
   - `POST /inbound/orders` — tạo phiếu nhập
   - `POST /inbound/orders/items` — thêm dòng hàng
   - `POST /slotting/suggest` — hệ thống gợi ý ô kệ phù hợp nhất
   - `POST /inbound/confirm-putaway` — nhân viên quét QR ô kệ xác nhận cất hàng
4. **Xuất kho**:
   - `POST /outbound/orders` → `POST /outbound/orders/items`
   - `POST /picking/optimize-route/{outbound_order_id}` — hệ thống tự chọn lô theo FEFO và tính lộ trình pick tối ưu
   - `POST /outbound/confirm-pick` — nhân viên quét QR ô kệ + lô hàng xác nhận đã lấy đúng
5. **Quét QR bất kỳ lúc nào**: `GET /warehouse/bins/scan/{qr_code}` — dùng cho cả nhân viên tìm hàng lẫn giám đốc kiểm tra tình trạng
6. **Gộp đơn (kho livestream)**: `POST /picking/batch` với danh sách `order_ids`
7. **Job định kỳ**: `POST /slotting/recompute-velocity/{warehouse_id}` — chạy cron hàng tuần (hoặc hàng ngày với kho livestream) để tính lại hạng A/B/C

## Việc cần làm tiếp (gợi ý, chưa có trong bản này)

- Xác thực/phân quyền (JWT + role: thủ kho / giám đốc / kế toán)
- WebSocket để đẩy cập nhật tồn kho realtime lên dashboard giám đốc
- Bảng `SERIAL_NUMBERS` cho ngành điện tử, `PRODUCT_VARIANTS` cho ngành may mặc
- Thay `manhattan_distance` trong `routing.py` bằng tra cứu shortest-path trên đồ thị kho thực tế (Dijkstra, cache sẵn) khi layout phức tạp hơn dạng lưới
- Alembic để quản lý migration khi schema thay đổi
