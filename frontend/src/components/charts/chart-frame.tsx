"use client";

import type { ReactNode } from "react";

import { EmptyState } from "@/components/async/empty-state";
import { ErrorCard } from "@/components/async/error-card";
import { Skeleton } from "@/components/async/skeleton";
import { useMounted } from "@/lib/use-mounted";

/**
 * Fixed-height frame that renders a chart's loading / error / empty / data states so
 * every chart gets them for free (the "no chart without its states" rule). The chart
 * itself is only mounted on the data path.
 */
export function ChartFrame({
  height = 240,
  loading,
  error,
  onRetry,
  isEmpty,
  emptyMessage = "No data for this range.",
  children,
}: {
  height?: number;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  isEmpty?: boolean;
  emptyMessage?: string;
  children: ReactNode;
}) {
  const mounted = useMounted();

  if (loading) return <Skeleton style={{ height }} className="w-full" />;
  if (error) return <ErrorCard message={error} onRetry={onRetry} />;
  if (isEmpty)
    return (
      <div style={{ height }} className="flex items-center justify-center">
        <EmptyState title="Nothing to chart" description={emptyMessage} className="border-0" />
      </div>
    );
  // Defer the chart until the client can measure it (ResponsiveContainer needs a box).
  return <div style={{ height }}>{mounted ? children : <Skeleton className="size-full" />}</div>;
}

/** Token-driven palette so chart series follow the theme (light/dark). */
export const CHART_COLORS = [
  "var(--primary)",
  "var(--success)",
  "var(--warning)",
  "var(--destructive)",
] as const;

/** Shared Recharts tooltip styling that respects the card tokens in both themes. */
export const tooltipStyle = {
  contentStyle: {
    background: "var(--popover)",
    border: "1px solid var(--border)",
    borderRadius: "0.5rem",
    color: "var(--popover-foreground)",
    fontSize: "0.8125rem",
  },
  labelStyle: { color: "var(--muted-foreground)" },
} as const;
