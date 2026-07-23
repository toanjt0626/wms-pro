import { ScanLine } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";

export default function ScanQR() {
  return (
    <div>
      <PageHeader
        title="Quét QR"
        description="Quét mã QR trên ô kệ để xem ngay thông tin lô hàng đang lưu tại đó."
      />

      <div className="max-w-sm mx-auto md:mx-0">
        <div className="aspect-square rounded-2xl bg-ink flex flex-col items-center justify-center gap-3 text-white/50">
          <ScanLine size={40} strokeWidth={1.5} />
          <p className="text-sm">Camera sẽ hiển thị ở đây</p>
        </div>
        <button className="w-full mt-4 bg-brand text-white rounded-lg py-3 text-sm font-medium">
          Mở camera quét mã
        </button>
      </div>
    </div>
  );
}
