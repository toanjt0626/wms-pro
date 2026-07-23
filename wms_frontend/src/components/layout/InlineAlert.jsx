import { AlertCircle, CheckCircle2 } from "lucide-react";

export default function InlineAlert({ type = "error", message, onClose }) {
  if (!message) return null;
  const isError = type === "error";
  return (
    <div
      className={[
        "flex items-start gap-2 rounded-lg border px-3 py-2 text-sm mb-4",
        isError
          ? "bg-danger-light border-danger/20 text-danger"
          : "bg-brand-light border-brand/20 text-brand",
      ].join(" ")}
    >
      {isError ? <AlertCircle size={16} className="mt-0.5 shrink-0" /> : <CheckCircle2 size={16} className="mt-0.5 shrink-0" />}
      <p className="flex-1">{message}</p>
      {onClose && (
        <button onClick={onClose} className="text-xs underline shrink-0">
          Đóng
        </button>
      )}
    </div>
  );
}
