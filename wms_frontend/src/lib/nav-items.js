import {
  ScanLine,
  LayoutDashboard,
  PackagePlus,
  PackageMinus,
  Map,
  BarChart3,
} from "lucide-react";

// Danh sách điều hướng chính - dùng chung cho Sidebar (desktop) và BottomNav (mobile)
// để đảm bảo 2 giao diện luôn đồng bộ, không lệch nhau khi thêm chức năng mới.
export const NAV_ITEMS = [
  { to: "/", label: "Tổng quan", icon: LayoutDashboard },
  { to: "/scan", label: "Quét QR", icon: ScanLine },
  { to: "/inbound", label: "Nhập kho", icon: PackagePlus },
  { to: "/outbound", label: "Xuất kho", icon: PackageMinus },
  { to: "/warehouse-map", label: "Bản đồ kho", icon: Map },
  { to: "/reports", label: "Báo cáo", icon: BarChart3 },
];
