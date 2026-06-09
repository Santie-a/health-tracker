"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { formatISODate } from "@/lib/time";

import { CHART_COLORS, ChartFrame, tooltipStyle } from "./chart-frame";

export interface LineSeries {
  key: string;
  label?: string;
  color?: string;
}

/**
 * Time-series line chart. `xKey` values are gateway dates/instants (UTC); ticks are
 * formatted to local by `xTickFormatter` (defaults to a local calendar-date label).
 * Loading/error/empty are handled by ChartFrame.
 */
export function TrendLine<T extends Record<string, unknown>>({
  data,
  xKey,
  lines,
  height,
  loading,
  error,
  onRetry,
  xTickFormatter = (v) => formatISODate(String(v), "MMM d"),
  yTickFormatter,
}: {
  data: T[] | undefined;
  xKey: keyof T & string;
  lines: LineSeries[];
  height?: number;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  xTickFormatter?: (value: unknown) => string;
  yTickFormatter?: (value: number) => string;
}) {
  return (
    <ChartFrame
      height={height}
      loading={loading}
      error={error}
      onRetry={onRetry}
      isEmpty={!data?.length}
    >
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis
            // recharts v3 brands dataKey to keys of the inferred row type; our generic
            // `keyof T & string` is equivalent but not assignable to the brand.
            dataKey={xKey as never}
            tickFormatter={xTickFormatter}
            tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
            stroke="var(--border)"
            minTickGap={24}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
            stroke="var(--border)"
            tickFormatter={yTickFormatter}
            width={44}
          />
          <Tooltip {...tooltipStyle} labelFormatter={(v) => xTickFormatter(v)} />
          {lines.map((line, i) => (
            <Line
              key={line.key}
              type="monotone"
              dataKey={line.key}
              name={line.label ?? line.key}
              stroke={line.color ?? CHART_COLORS[i % CHART_COLORS.length]}
              strokeWidth={2}
              dot={false}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}
