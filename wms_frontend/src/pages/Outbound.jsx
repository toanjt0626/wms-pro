import { PackageMinus } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import EmptyState from "../components/layout/EmptyState";

export default function Outbound() {
  return (
    <div>
      <PageHeader
        title="Xuất kho"
        description="Danh sách phiếu xuất sẽ hiển thị ở đây, nối vào API /outbound ở bước tiếp theo."
        action={
          <button className="bg-brand text-white text-sm font-medium rounded-lg px-4 py-2">
            + Tạo phiếu xuất
          </button>
        }
      />
      <EmptyState
        icon={PackageMinus}
        title="Chưa có phiếu xuất nào"
        description="Tạo phiếu xuất để hệ thống tự gợi ý lô hàng (FEFO) và lộ trình pick tối ưu."
      />
    </div>
  );
}
