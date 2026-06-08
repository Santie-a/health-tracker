"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceArea,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CHART_COLORS, ChartFrame, tooltipStyle } from "./chart-frame";

export interface BarSeries {
  key: string;
  label?: string;
  color?: string;
}

/**
 * Categorical/grouped bar chart (e.g. weekly sets per muscle). Optional `targetBand`
 * draws a shaded reference range (the 10–20 sets/week target). Per-bar coloring via
 * `colorFor` lets a single series flag in/under/over the band.
 */
export function GroupedBars<T extends Record<string, unknown>>({
  data,
  xKey,
  bars,
  height,
  loading,
  error,
  onRetry,
  targetBand,
  colorFor,
  xTickFormatter,
}: {
  data: T[] | undefined;
  xKey: keyof T & string;
  bars: BarSeries[];
  height?: number;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  targetBand?: { from: number; to: number };
  colorFor?: (row: T) => string;
  xTickFormatter?: (value: unknown) => string;
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
        <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis
            // recharts v3 brands dataKey to keys of the inferred row type; our generic
            // `keyof T & string` is equivalent but not assignable to the brand.
            dataKey={xKey as never}
            tickFormatter={xTickFormatter}
            tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
            stroke="var(--border)"
            interval={0}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
            stroke="var(--border)"
            width={32}
            allowDecimals={false}
          />
          <Tooltip {...tooltipStyle} cursor={{ fill: "var(--muted)", opacity: 0.4 }} />
          {targetBand ? (
            <ReferenceArea
              y1={targetBand.from}
              y2={targetBand.to}
              fill="var(--success)"
              fillOpacity={0.1}
            />
          ) : null}
          {bars.map((bar, i) => (
            <Bar
              key={bar.key}
              dataKey={bar.key}
              name={bar.label ?? bar.key}
              fill={bar.color ?? CHART_COLORS[i % CHART_COLORS.length]}
              radius={[3, 3, 0, 0]}
            >
              {colorFor ? data?.map((row, ri) => <Cell key={ri} fill={colorFor(row)} />) : null}
            </Bar>
          ))}
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}
