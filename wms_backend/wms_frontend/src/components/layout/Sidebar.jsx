import { NavLink } from "react-router-dom";
import { Boxes } from "lucide-react";
import { NAV_ITEMS } from "../../lib/nav-items";

export default function Sidebar() {
  return (
    <aside className="hidden md:flex md:flex-col md:w-60 md:shrink-0 bg-ink text-white/90 min-h-screen">
      <div className="flex items-center gap-2 px-5 h-16 border-b border-white/10">
        <Boxes size={22} className="text-brand shrink-0" strokeWidth={2} />
        <span className="font-display font-semibold text-[15px] tracking-tight text-white">
          Kho Vận
        </span>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              [
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors",
                isActive
                  ? "bg-brand/15 text-white font-medium"
                  : "text-white/60 hover:text-white hover:bg-white/5",
              ].join(" ")
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={18} strokeWidth={isActive ? 2.25 : 1.75} />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="px-5 py-4 border-t border-white/10 text-xs text-white/40">
        Kho A · Trung tâm
      </div>
    </aside>
  );
}
