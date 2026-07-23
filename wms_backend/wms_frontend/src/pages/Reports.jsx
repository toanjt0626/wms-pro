import { BarChart3 } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import EmptyState from "../components/layout/EmptyState";

export default function Reports() {
  return (
    <div>
      <PageHeader
        title="Báo cáo"
        description="Báo cáo tồn kho, tốc độ luân chuyển, và lịch sử giao dịch."
      />
      <EmptyState
        icon={BarChart3}
        title="Chưa có báo cáo nào"
        description="Các biểu đồ sẽ hiển thị ở đây khi nối vào dữ liệu InventoryTransaction thật."
      />
    </div>
  );
}
