import { useEffect, useState, Fragment } from "react";
import { Plus, MapPin, PackageCheck, Loader2 } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import EmptyState from "../components/layout/EmptyState";
import StatusBadge from "../components/layout/StatusBadge";
import InlineAlert from "../components/layout/InlineAlert";
import { api } from "../lib/api";

export default function Inbound() {
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [warehouse, setWarehouse] = useState(null);
  const [selectedOrderId, setSelectedOrderId] = useState(null);
  const [orderDetail, setOrderDetail] = useState(null);

  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [showNewOrderForm, setShowNewOrderForm] = useState(false);
  const [newOrderCode, setNewOrderCode] = useState("");

  const [newItem, setNewItem] = useState({ product_id: "", expected_qty: "" });

  const [suggestingItemId, setSuggestingItemId] = useState(null);
  const [suggestions, setSuggestions] = useState({});

  const [putawayForm, setPutawayForm] = useState({
    item_id: "",
    lot_number: "",
    expiry_date: "",
    bin_qr_code: "",
    quantity: "",
  });
  const [submittingPutaway, setSubmittingPutaway] = useState(false);

  useEffect(() => {
    loadOrders();
    api.getProducts().then(setProducts).catch((e) => setError(e.message));
    api
      .getWarehouses()
      .then((whs) => setWarehouse(whs[0] || null))
      .catch((e) => setError(e.message));
  }, []);

  async function loadOrders() {
    setLoadingList(true);
    try {
      const data = await api.getInboundOrders();
      setOrders(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingList(false);
    }
  }

  async function selectOrder(id) {
    setSelectedOrderId(id);
    setLoadingDetail(true);
    setSuggestions({});
    setError("");
    try {
      const data = await api.getInboundOrder(id);
      setOrderDetail(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingDetail(false);
    }
  }

  async function handleCreateOrder(e) {
    e.preventDefault();
    if (!newOrderCode.trim()) return;
    setError("");
    try {
      const order = await api.createInboundOrder(newOrderCode.trim());
      setNewOrderCode("");
      setShowNewOrderForm(false);
      await loadOrders();
      selectOrder(order.id);
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleAddItem(e) {
    e.preventDefault();
    if (!newItem.product_id || !newItem.expected_qty) return;
    setError("");
    try {
      await api.addInboundItem({
        inbound_order_id: selectedOrderId,
        product_id: newItem.product_id,
        expected_qty: Number(newItem.expected_qty),
      });
      setNewItem({ product_id: "", expected_qty: "" });
      await selectOrder(selectedOrderId);
      await loadOrders();
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleSuggest(item) {
    if (!warehouse) return;
    setSuggestingItemId(item.id);
    setError("");
    try {
      const remaining = item.expected_qty - item.received_qty;
      const res = await api.suggestPutaway({
        warehouse_id: warehouse.id,
        product_id: item.product_id,
        quantity: remaining > 0 ? remaining : item.expected_qty,
      });
      setSuggestions((prev) => ({ ...prev, [item.id]: res.suggestions }));
    } catch (e) {
      setError(e.message);
    } finally {
      setSuggestingItemId(null);
    }
  }

  function pickSuggestion(item, suggestion) {
    setPutawayForm((prev) => ({
      ...prev,
      item_id: item.id,
      bin_qr_code: suggestion.qr_code,
      quantity: String(item.expected_qty - item.received_qty),
    }));
    document.getElementById("putaway-form")?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  async function handleConfirmPutaway(e) {
    e.preventDefault();
    const item = orderDetail?.items.find((i) => i.id === putawayForm.item_id);
    if (!item || !putawayForm.bin_qr_code || !putawayForm.quantity || !putawayForm.lot_number) {
      setError("Vui lòng điền đủ: dòng hàng, số lô, mã QR ô kệ, số lượng.");
      return;
    }
    setSubmittingPutaway(true);
    setError("");
    setSuccess("");
    try {
      const lot = await api.createLot({
        product_id: item.product_id,
        lot_number: putawayForm.lot_number,
        expiry_date: putawayForm.expiry_date || null,
      });
      const result = await api.confirmPutaway({
        inbound_order_item_id: item.id,
        lot_id: lot.id,
        bin_qr_code: putawayForm.bin_qr_code,
        quantity: Number(putawayForm.quantity),
        created_by: "web-ui",
      });
      setSuccess(`Đã cất ${putawayForm.quantity} vào ô ${result.bin_location_code}.`);
      setPutawayForm({ item_id: "", lot_number: "", expiry_date: "", bin_qr_code: "", quantity: "" });
      setSuggestions({});
      await selectOrder(selectedOrderId);
      await loadOrders();
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmittingPutaway(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Nhập kho"
        description="Tạo phiếu, thêm dòng hàng, xem gợi ý vị trí và xác nhận cất hàng qua mã QR."
        action={
          <button
            onClick={() => setShowNewOrderForm((v) => !v)}
            className="flex items-center gap-1.5 bg-brand text-white text-sm font-medium rounded-lg px-4 py-2"
          >
            <Plus size={16} /> Tạo phiếu nhập
          </button>
        }
      />

      <InlineAlert type="error" message={error} onClose={() => setError("")} />
      <InlineAlert type="success" message={success} onClose={() => setSuccess("")} />

      {showNewOrderForm && (
        <form
          onSubmit={handleCreateOrder}
          className="flex items-center gap-2 mb-4 bg-surface border border-border rounded-xl p-3"
        >
          <input
            autoFocus
            value={newOrderCode}
            onChange={(e) => setNewOrderCode(e.target.value)}
            placeholder="Mã phiếu, vd: PN-002"
            className="flex-1 border border-border rounded-lg px-3 py-2 text-sm code-tag"
          />
          <button type="submit" className="bg-brand text-white text-sm font-medium rounded-lg px-4 py-2">
            Tạo
          </button>
        </form>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-4">
        <div className="bg-surface border border-border rounded-xl overflow-hidden">
          <div className="px-4 py-3 border-b border-border">
            <h2 className="font-display font-semibold text-sm text-text">Danh sách phiếu</h2>
          </div>
          {loadingList ? (
            <div className="p-6 flex justify-center text-text-muted">
              <Loader2 size={18} className="animate-spin" />
            </div>
          ) : orders.length === 0 ? (
            <p className="text-sm text-text-muted p-4">Chưa có phiếu nhập nào.</p>
          ) : (
            <ul className="divide-y divide-border max-h-[70vh] overflow-y-auto">
              {orders.map((o) => (
                <li key={o.id}>
                  <button
                    onClick={() => selectOrder(o.id)}
                    className={[
                      "w-full text-left px-4 py-3 hover:bg-paper transition-colors",
                      selectedOrderId === o.id ? "bg-brand-light" : "",
                    ].join(" ")}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="code-tag text-sm font-medium text-text">{o.code}</span>
                      <StatusBadge status={o.status} />
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div>
          {!selectedOrderId ? (
            <EmptyState
              icon={PackageCheck}
              title="Chọn một phiếu nhập để xem chi tiết"
              description="Hoặc tạo phiếu mới bằng nút ở trên."
            />
          ) : loadingDetail ? (
            <div className="p-10 flex justify-center text-text-muted">
              <Loader2 size={22} className="animate-spin" />
            </div>
          ) : (
            orderDetail && (
              <div className="space-y-4">
                <div className="bg-surface border border-border rounded-xl p-4">
                  <div className="flex items-center justify-between mb-4">
                    <span className="code-tag font-semibold text-text">{orderDetail.code}</span>
                    <StatusBadge status={orderDetail.status} />
                  </div>

                  {orderDetail.items.length === 0 ? (
                    <p className="text-sm text-text-muted">Chưa có dòng hàng nào.</p>
                  ) : (
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-left text-text-muted border-b border-border">
                          <th className="font-normal pb-2">Sản phẩm</th>
                          <th className="font-normal pb-2 text-right">Đã nhận / Dự kiến</th>
                          <th className="font-normal pb-2 text-right"></th>
                        </tr>
                      </thead>
                      <tbody>
                        {orderDetail.items.map((item) => (
                          <Fragment key={item.id}>
                            <tr className="border-b border-border/60">
                              <td className="py-2.5">
                                <p className="text-text">{item.product_name}</p>
                                <p className="code-tag text-xs text-text-muted">{item.product_sku}</p>
                              </td>
                              <td className="py-2.5 text-right">
                                <span
                                  className={
                                    item.received_qty >= item.expected_qty ? "text-brand" : "text-text"
                                  }
                                >
                                  {item.received_qty}
                                </span>
                                <span className="text-text-muted"> / {item.expected_qty}</span>
                              </td>
                              <td className="py-2.5 text-right">
                                {item.received_qty < item.expected_qty && (
                                  <button
                                    onClick={() => handleSuggest(item)}
                                    disabled={suggestingItemId === item.id}
                                    className="inline-flex items-center gap-1 text-xs text-brand font-medium hover:underline disabled:opacity-50"
                                  >
                                    {suggestingItemId === item.id ? (
                                      <Loader2 size={13} className="animate-spin" />
                                    ) : (
                                      <MapPin size={13} />
                                    )}
                                    Gợi ý vị trí
                                  </button>
                                )}
                              </td>
                            </tr>
                            {suggestions[item.id] && (
                              <tr>
                                <td colSpan={3} className="pb-3">
                                  <div className="flex flex-wrap gap-2 pt-1">
                                    {suggestions[item.id].map((s) => (
                                      <button
                                        key={s.bin_id}
                                        onClick={() => pickSuggestion(item, s)}
                                        className="text-left border border-border rounded-lg px-3 py-2 hover:border-brand hover:bg-brand-light transition-colors"
                                      >
                                        <p className="code-tag text-xs font-medium text-text">
                                          {s.location_code}
                                        </p>
                                        <p className="text-[11px] text-text-muted">
                                          điểm {s.score.toFixed(2)}
                                        </p>
                                      </button>
                                    ))}
                                  </div>
                                </td>
                              </tr>
                            )}
                          </Fragment>
                        ))}
                      </tbody>
                    </table>
                  )}

                  <form
                    onSubmit={handleAddItem}
                    className="flex flex-wrap items-center gap-2 mt-4 pt-4 border-t border-border"
                  >
                    <select
                      value={newItem.product_id}
                      onChange={(e) => setNewItem((p) => ({ ...p, product_id: e.target.value }))}
                      className="border border-border rounded-lg px-3 py-2 text-sm flex-1 min-w-[160px]"
                    >
                      <option value="">Chọn sản phẩm...</option>
                      {products.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.name} ({p.sku})
                        </option>
                      ))}
                    </select>
                    <input
                      type="number"
                      min="1"
                      placeholder="Số lượng dự kiến"
                      value={newItem.expected_qty}
                      onChange={(e) => setNewItem((p) => ({ ...p, expected_qty: e.target.value }))}
                      className="border border-border rounded-lg px-3 py-2 text-sm w-40"
                    />
                    <button type="submit" className="bg-ink text-white text-sm font-medium rounded-lg px-4 py-2">
                      + Thêm dòng hàng
                    </button>
                  </form>
                </div>

                <div id="putaway-form" className="bg-surface border border-border rounded-xl p-4">
                  <h3 className="font-display font-semibold text-sm text-text mb-3">
                    Xác nhận cất hàng (quét QR ô kệ)
                  </h3>
                  <form onSubmit={handleConfirmPutaway} className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <select
                      value={putawayForm.item_id}
                      onChange={(e) => setPutawayForm((p) => ({ ...p, item_id: e.target.value }))}
                      className="border border-border rounded-lg px-3 py-2 text-sm sm:col-span-2"
                    >
                      <option value="">Chọn dòng hàng...</option>
                      {orderDetail.items.map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.product_name} — còn thiếu {item.expected_qty - item.received_qty}
                        </option>
                      ))}
                    </select>
                    <input
                      placeholder="Số lô, vd: LOT-2607"
                      value={putawayForm.lot_number}
                      onChange={(e) => setPutawayForm((p) => ({ ...p, lot_number: e.target.value }))}
                      className="border border-border rounded-lg px-3 py-2 text-sm code-tag"
                    />
                    <input
                      type="date"
                      value={putawayForm.expiry_date}
                      onChange={(e) => setPutawayForm((p) => ({ ...p, expiry_date: e.target.value }))}
                      className="border border-border rounded-lg px-3 py-2 text-sm"
                      title="Hạn dùng (bỏ trống nếu không cần)"
                    />
                    <input
                      placeholder="Mã QR ô kệ, vd: QR-A1-01-01"
                      value={putawayForm.bin_qr_code}
                      onChange={(e) => setPutawayForm((p) => ({ ...p, bin_qr_code: e.target.value }))}
                      className="border border-border rounded-lg px-3 py-2 text-sm code-tag"
                    />
                    <input
                      type="number"
                      min="1"
                      placeholder="Số lượng"
                      value={putawayForm.quantity}
                      onChange={(e) => setPutawayForm((p) => ({ ...p, quantity: e.target.value }))}
                      className="border border-border rounded-lg px-3 py-2 text-sm"
                    />
                    <button
                      type="submit"
                      disabled={submittingPutaway}
                      className="sm:col-span-2 bg-brand text-white text-sm font-medium rounded-lg py-2.5 disabled:opacity-60 flex items-center justify-center gap-2"
                    >
                      {submittingPutaway && <Loader2 size={15} className="animate-spin" />}
                      Xác nhận cất hàng
                    </button>
                  </form>
                  <p className="text-xs text-text-muted mt-2">
                    Trường "Mã QR ô kệ" sẽ được thay bằng camera quét thật ở bước tiếp theo — hiện gõ tay
                    hoặc bấm vào một ô gợi ý vị trí phía trên để điền tự động.
                  </p>
                </div>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}
