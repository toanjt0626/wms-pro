import { Search, Bell, ChevronRight, Boxes } from "lucide-react";

// breadcrumb được truyền vào dạng mảng, vd: ["KHO-A", "Z1", "A1-02-03"]
// Hiển thị bằng font mono để phản ánh đúng cách mã vị trí thực tế trong kho
// được đặt tên - đây là điểm nhấn xuyên suốt sản phẩm, không phải breadcrumb thường.
export default function Topbar({ breadcrumb = ["KHO-A"], title }) {
  return (
    <header className="h-16 shrink-0 border-b border-border bg-surface flex items-center justify-between px-4 md:px-6 gap-3">
      <div className="flex items-center gap-3 min-w-0">
        <div className="md:hidden flex items-center gap-2 shrink-0">
          <Boxes size={20} className="text-brand" strokeWidth={2} />
        </div>

        <div className="hidden md:flex items-center gap-1.5 code-tag text-[13px] text-text-muted overflow-hidden">
          {breadcrumb.map((part, i) => (
            <span key={i} className="flex items-center gap-1.5 shrink-0">
              {i > 0 && <ChevronRight size={13} className="text-border" />}
              <span className={i === breadcrumb.length - 1 ? "text-text font-medium" : ""}>
                {part}
              </span>
            </span>
          ))}
        </div>

        {title && (
          <h1 className="md:hidden font-display font-semibold text-[16px] text-text truncate">
            {title}
          </h1>
        )}
      </div>

      <div className="flex items-center gap-1 shrink-0">
        <button
          className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border text-text-muted text-sm hover:bg-paper transition-colors"
          aria-label="Tìm kiếm"
        >
          <Search size={15} />
          <span className="text-xs text-text-muted/70">Tìm SKU, vị trí...</span>
        </button>
        <button
          className="sm:hidden p-2 rounded-lg text-text-muted hover:bg-paper transition-colors"
          aria-label="Tìm kiếm"
        >
          <Search size={19} />
        </button>
        <button
          className="relative p-2 rounded-lg text-text-muted hover:bg-paper transition-colors"
          aria-label="Thông báo"
        >
          <Bell size={19} />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-danger" />
        </button>
        <div className="w-8 h-8 rounded-full bg-brand text-white flex items-center justify-center text-xs font-medium ml-1">
          NT
        </div>
      </div>
    </header>
  );
}
