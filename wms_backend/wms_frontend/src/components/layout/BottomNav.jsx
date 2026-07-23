import { NavLink } from "react-router-dom";
import { NAV_ITEMS } from "../../lib/nav-items";

export default function BottomNav() {
  return (
    <nav className="md:hidden fixed bottom-0 inset-x-0 h-16 bg-ink border-t border-white/10 flex items-stretch z-20 pb-[env(safe-area-inset-bottom)]">
      {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === "/"}
          className="flex-1 flex flex-col items-center justify-center gap-0.5"
        >
          {({ isActive }) => (
            <>
              <Icon
                size={20}
                strokeWidth={isActive ? 2.25 : 1.75}
                className={isActive ? "text-brand" : "text-white/45"}
              />
              <span
                className={[
                  "text-[10px] leading-none",
                  isActive ? "text-white font-medium" : "text-white/45",
                ].join(" ")}
              >
                {label}
              </span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
}
