export default function NeonInput({ label, id, className = "", ...props }) {
  const inputId = id || `neon-input-${label?.toLowerCase().replace(/\s+/g, "-")}`;

  return (
    <div className="neon-input-group">
      <input
        id={inputId}
        className={`neon-input ${className}`}
        placeholder=" "
        {...props}
      />
      {label && (
        <label htmlFor={inputId} className="neon-floating-label">
          {label}
        </label>
      )}
    </div>
  );
}
