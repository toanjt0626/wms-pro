import { Map } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import EmptyState from "../components/layout/EmptyState";

export default function WarehouseMap() {
  return (
    <div>
      <PageHeader
        title="Bản đồ kho"
        description="Sơ đồ trực quan các khu vực, dãy kệ, và tình trạng đầy/trống."
      />
      <EmptyState
        icon={Map}
        title="Bản đồ kho sẽ hiển thị ở đây"
        description="Sẽ dựng dạng heatmap theo khu vực, nối vào dữ liệu thật ở bước tiếp theo."
      />
    </div>
  );
}
