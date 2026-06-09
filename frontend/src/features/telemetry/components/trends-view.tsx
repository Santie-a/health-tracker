"use client";

import { useMemo, useState } from "react";
import type { UseQueryResult } from "@tanstack/react-query";

import { TrendLine } from "@/components/charts/trend-line";
import { SectionCard } from "@/components/ui/section-card";
import { Segmented } from "@/components/ui/segmented";
import { ApiError } from "@/lib/query/fetcher";
import { formatInstant } from "@/lib/time";

import { useBodyComposition, useDailyMetric, useSleepSeries } from "../hooks";

const RANGES = [
  { value: "7", label: "7d" },
  { value: "30", label: "30d" },
  { value: "90", label: "90d" },
] as const;

const METRICS = [
  { key: "steps", label: "Steps", agg: "sum" as const },
  { key: "stress", label: "Stress", agg: "avg" as const },
  { key: "heart_rate", label: "Heart rate", agg: "avg" as const },
  { key: "spo2", label: "SpO₂", agg: "avg" as const },
  { key: "energy_expenditure", label: "Energy", agg: "sum" as const },
];

function rangeDates(days: number): { from: string; to: string } {
  const to = new Date();
  const from = new Date(to.getTime() - days * 86_400_000);
  return { from: from.toISOString(), to: to.toISOString() };
}

/** Map a query's error to a friendly string for the chart frame (null when fine). */
function errOf(q: UseQueryResult): string | null {
  if (!q.isError) return null;
  return q.error instanceof ApiError ? q.error.friendly : "Couldn't load this.";
}

const dayTick = (v: unknown) => formatInstant(String(v), "MMM d");

export function TrendsView() {
  const [days, setDays] = useState<string>("30");
  const [metric, setMetric] = useState<string>("steps");
  const { from, to } = useMemo(() => rangeDates(Number(days)), [days]);

  const body = useBodyComposition(from, to);
  const sleep = useSleepSeries(from, to);
  const activity = useDailyMetric(metric, from, to);

  const sleepData = (sleep.data ?? []).map((n) => ({
    day: n.day,
    total_h: n.total_min != null ? +(n.total_min / 60).toFixed(2) : null,
    deep_h: n.deep_min != null ? +(n.deep_min / 60).toFixed(2) : null,
  }));

  const metricCfg = METRICS.find((m) => m.key === metric)!;
  const activityData = (activity.data ?? []).map((r) => ({
    day: r.day,
    value: metricCfg.agg === "sum" ? r.sum : r.avg,
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Trends</h1>
        <Segmented options={[...RANGES]} value={days} onChange={setDays} size="sm" />
      </div>

      <SectionCard title="Body composition">
        <TrendLine
          data={body.data}
          xKey="ts"
          xTickFormatter={dayTick}
          loading={body.isPending}
          error={errOf(body)}
          onRetry={() => body.refetch()}
          lines={[
            { key: "weight_kg", label: "Weight (kg)" },
            { key: "skeletal_muscle_kg", label: "Muscle (kg)", color: "var(--success)" },
            { key: "body_fat_pct", label: "Body fat (%)", color: "var(--warning)" },
          ]}
        />
      </SectionCard>

      <SectionCard title="Sleep">
        <TrendLine
          data={sleepData}
          xKey="day"
          loading={sleep.isPending}
          error={errOf(sleep)}
          onRetry={() => sleep.refetch()}
          yTickFormatter={(v) => `${v}h`}
          lines={[
            { key: "total_h", label: "Total (h)" },
            { key: "deep_h", label: "Deep (h)", color: "var(--success)" },
          ]}
        />
      </SectionCard>

      <SectionCard
        title="Activity"
        action={
          <Segmented
            options={METRICS.map((m) => ({ value: m.key, label: m.label }))}
            value={metric}
            onChange={setMetric}
            size="sm"
          />
        }
      >
        <TrendLine
          data={activityData}
          xKey="day"
          loading={activity.isPending}
          error={errOf(activity)}
          onRetry={() => activity.refetch()}
          lines={[{ key: "value", label: metricCfg.label }]}
        />
      </SectionCard>
    </div>
  );
}
