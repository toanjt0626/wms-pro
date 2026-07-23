const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Lỗi máy chủ (${res.status})`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Sản phẩm
  getProducts: () => request("/products"),
  getProductLots: (productId) => request(`/products/${productId}/lots`),
  createLot: (payload) => request("/products/lots", { method: "POST", body: JSON.stringify(payload) }),

  // Kho
  getWarehouses: () => request("/warehouse/warehouses"),
  scanBin: (qrCode) => request(`/warehouse/bins/scan/${encodeURIComponent(qrCode)}`),

  // Nhập kho
  getInboundOrders: () => request("/inbound/orders"),
  getInboundOrder: (id) => request(`/inbound/orders/${id}`),
  createInboundOrder: (code) =>
    request("/inbound/orders", { method: "POST", body: JSON.stringify({ code }) }),
  addInboundItem: (payload) =>
    request("/inbound/orders/items", { method: "POST", body: JSON.stringify(payload) }),
  suggestPutaway: (payload) =>
    request("/slotting/suggest", { method: "POST", body: JSON.stringify(payload) }),
  confirmPutaway: (payload) =>
    request("/inbound/confirm-putaway", { method: "POST", body: JSON.stringify(payload) }),

  // Xuất kho (dùng ở bước tiếp theo)
  getOutboundOrders: () => request("/outbound/orders"),
  getOutboundOrder: (id) => request(`/outbound/orders/${id}`),
  createOutboundOrder: (payload) =>
    request("/outbound/orders", { method: "POST", body: JSON.stringify(payload) }),
  addOutboundItem: (payload) =>
    request("/outbound/orders/items", { method: "POST", body: JSON.stringify(payload) }),
  optimizeRoute: (orderId, layoutComplexity = "simple") =>
    request(`/picking/optimize-route/${orderId}?layout_complexity=${layoutComplexity}`, {
      method: "POST",
    }),
  confirmPick: (payload) =>
    request("/outbound/confirm-pick", { method: "POST", body: JSON.stringify(payload) }),
};
