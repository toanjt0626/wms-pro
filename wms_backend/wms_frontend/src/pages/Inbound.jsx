import { PackagePlus } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import EmptyState from "../components/layout/EmptyState";

export default function Inbound() {
  return (
    <div>
      <PageHeader
        title="Nhập kho"
        description="Danh sách phiếu nhập sẽ hiển thị ở đây, nối vào API /inbound ở bước tiếp theo."
        action={
          <button className="bg-brand text-white text-sm font-medium rounded-lg px-4 py-2">
            + Tạo phiếu nhập
          </button>
        }
      />
      <EmptyState
        icon={PackagePlus}
        title="Chưa có phiếu nhập nào"
        description="Tạo phiếu nhập đầu tiên để bắt đầu theo dõi hàng về kho."
      />
    </div>
  );
}
