import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

/**
 * A single metric tile. Null/undefined values render a greyed "—" with an optional
 * hint, so a missing telemetry signal (no watch data) reads as absent, not broken —
 * never an error. Pass a `format` to render numbers consistently.
 */
export function StatCard({
  label,
  value,
  unit,
  icon,
  hint,
  emptyHint = "No data",
  format,
  className,
}: {
  label: string;
  value: number | string | null | undefined;
  unit?: string;
  icon?: ReactNode;
  hint?: string;
  emptyHint?: string;
  format?: (n: number) => string;
  className?: string;
}) {
  const isEmpty = value === null || value === undefined || value === "";
  const display = isEmpty
    ? "—"
    : typeof value === "number"
      ? format
        ? format(value)
        : String(value)
      : value;

  return (
    <div className={cn("bg-card rounded-xl border p-4", className)}>
      <div className="text-muted-foreground flex items-center gap-1.5 text-xs font-medium">
        {icon}
        {label}
      </div>
      <div className="mt-1 flex items-baseline gap-1">
        <span
          className={cn(
            "text-2xl font-semibold tracking-tight tabular-nums",
            isEmpty && "text-muted-foreground",
          )}
        >
          {display}
        </span>
        {!isEmpty && unit ? <span className="text-muted-foreground text-sm">{unit}</span> : null}
      </div>
      {(isEmpty ? emptyHint : hint) ? (
        <p className="text-muted-foreground mt-0.5 text-xs">{isEmpty ? emptyHint : hint}</p>
      ) : null}
    </div>
  );
}
