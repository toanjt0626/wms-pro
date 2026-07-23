export default function EmptyState({ icon: Icon, title, description }) {
  return (
    <div className="border border-dashed border-border rounded-xl bg-surface flex flex-col items-center justify-center text-center py-16 px-6">
      {Icon && (
        <div className="w-11 h-11 rounded-full bg-brand-light flex items-center justify-center mb-3">
          <Icon size={20} className="text-brand" strokeWidth={1.75} />
        </div>
      )}
      <p className="font-medium text-text text-sm">{title}</p>
      {description && (
        <p className="text-text-muted text-sm mt-1 max-w-sm">{description}</p>
      )}
    </div>
  );
}
