import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import BottomNav from "./BottomNav";
import { NAV_ITEMS } from "../../lib/nav-items";

export default function MainLayout() {
  const location = useLocation();
  const current = NAV_ITEMS.find((n) =>
    n.to === "/" ? location.pathname === "/" : location.pathname.startsWith(n.to)
  );

  return (
    <div className="min-h-screen flex bg-paper">
      <Sidebar />

      <div className="flex-1 min-w-0 flex flex-col">
        <Topbar breadcrumb={["KHO-A", current?.label ?? ""]} title={current?.label} />

        {/* pb-20 chừa chỗ cho BottomNav trên mobile để nội dung không bị che */}
        <main className="flex-1 min-w-0 p-4 md:p-6 pb-20 md:pb-6">
          <Outlet />
        </main>
      </div>

      <BottomNav />
    </div>
  );
}
