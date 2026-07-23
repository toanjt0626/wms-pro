import { Package, AlertTriangle, TrendingUp, Clock } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";

const STATS = [
  { label: "Tổng SKU đang lưu kho", value: "1.284", icon: Package, tone: "brand" },
  { label: "Sắp hết hạn (7 ngày)", value: "12", icon: AlertTriangle, tone: "warning" },
  { label: "Đơn xuất hôm nay", value: "356", icon: TrendingUp, tone: "brand" },
  { label: "Đơn đang chờ pick", value: "24", icon: Clock, tone: "danger" },
];

const toneClasses = {
  brand: "bg-brand-light text-brand",
  warning: "bg-warning-light text-warning",
  danger: "bg-danger-light text-danger",
};

export default function Dashboard() {
  return (
    <div>
      <PageHeader
        title="Tổng quan kho"
        description="Số liệu dưới đây là dữ liệu mẫu - sẽ được nối vào API thật ở bước tiếp theo."
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        {STATS.map(({ label, value, icon: Icon, tone }) => (
          <div key={label} className="bg-surface border border-border rounded-xl p-4">
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center mb-3 ${toneClasses[tone]}`}>
              <Icon size={16} strokeWidth={2} />
            </div>
            <p className="font-display font-semibold text-2xl text-text leading-none">{value}</p>
            <p className="text-xs text-text-muted mt-1.5">{label}</p>
          </div>
        ))}
      </div>

      <div className="bg-surface border border-border rounded-xl p-5">
        <h2 className="font-display font-semibold text-text mb-1">Bản đồ tồn kho theo khu vực</h2>
        <p className="text-sm text-text-muted mb-4">
          Sẽ hiển thị heatmap các khu vực đầy/trống ở bước gắn chức năng thật.
        </p>
        <div className="h-40 rounded-lg bg-paper border border-dashed border-border flex items-center justify-center text-text-muted text-sm">
          Khu vực hiển thị bản đồ kho
        </div>
      </div>
    </div>
  );
}
