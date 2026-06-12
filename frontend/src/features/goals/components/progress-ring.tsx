/**
 * Circular progress indicator for a goal. `value` is 0..1 along baseline→target.
 * When the fraction is unknown (no numeric target), pass `value={null}` to render a
 * faint full track with the center label only — never a broken/zero ring.
 */
export function ProgressRing({
  value,
  color = "var(--primary)",
  size = 96,
  stroke = 9,
  label,
  sublabel,
}: {
  value: number | null;
  color?: string;
  size?: number;
  stroke?: number;
  label?: string;
  sublabel?: string;
}) {
  const r = (size - stroke) / 2;
  const circumference = 2 * Math.PI * r;
  const pct = value == null ? 0 : Math.max(0, Math.min(1, value));
  const dash = pct * circumference;

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="var(--border)"
          strokeWidth={stroke}
        />
        {value != null ? (
          <circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke={color}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={`${dash} ${circumference - dash}`}
            className="transition-[stroke-dasharray] duration-500"
          />
        ) : null}
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        {label ? (
          <span className="text-lg leading-none font-semibold tabular-nums">{label}</span>
        ) : null}
        {sublabel ? (
          <span className="text-muted-foreground mt-0.5 text-[10px] leading-none">{sublabel}</span>
        ) : null}
      </div>
    </div>
  );
}
