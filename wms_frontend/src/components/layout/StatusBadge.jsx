const STATUS_STYLES = {
  draft: "bg-paper text-text-muted border-border",
  confirmed: "bg-brand-light text-brand border-brand/20",
  receiving: "bg-warning-light text-warning border-warning/20",
  picking: "bg-warning-light text-warning border-warning/20",
  completed: "bg-brand-light text-brand border-brand/20",
  packed: "bg-brand-light text-brand border-brand/20",
  pending: "bg-paper text-text-muted border-border",
};

const STATUS_LABELS = {
  draft: "Nháp",
  confirmed: "Đã xác nhận",
  receiving: "Đang nhận hàng",
  picking: "Đang pick hàng",
  completed: "Hoàn tất",
  packed: "Đã đóng gói",
  pending: "Chờ xử lý",
};

export default function StatusBadge({ status }) {
  return (
    <span
      className={[
        "inline-flex items-center px-2 py-0.5 rounded-full border text-xs font-medium",
        STATUS_STYLES[status] || STATUS_STYLES.draft,
      ].join(" ")}
    >
      {STATUS_LABELS[status] || status}
    </span>
  );
}
