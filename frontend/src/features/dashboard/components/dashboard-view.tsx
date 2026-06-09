"use client";

import { useState } from "react";

import { AsyncBoundary } from "@/components/async/async-boundary";
import { QueryState } from "@/components/async/query-state";
import { Skeleton } from "@/components/async/skeleton";
import { todayISODate } from "@/lib/time";

import { DateNav } from "@/components/date-nav";

import { useDashboard } from "../hooks";
import { NutritionSummary } from "./nutrition-summary";
import { RecommendationsSummary } from "./recommendations-summary";
import { TelemetrySummary } from "./telemetry-summary";
import { TrainingSummary } from "./training-summary";

function DashboardSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-32 w-full" />
      <div className="grid gap-4 lg:grid-cols-2">
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-40 w-full" />
      </div>
      <Skeleton className="h-40 w-full" />
    </div>
  );
}

/**
 * The Today view: one `GET /dashboard?date=` call rendered into independent sections.
 * Each section is wrapped in its own AsyncBoundary so a render failure in one shows a
 * contained error + retry while the rest of the day still renders.
 */
export function DashboardView() {
  const [date, setDate] = useState(todayISODate);
  const query = useDashboard(date);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Today</h1>
        <DateNav date={date} onChange={setDate} />
      </div>

      <QueryState query={query} loading={<DashboardSkeleton />}>
        {(day) => (
          <div className="space-y-4">
            <AsyncBoundary>
              <TelemetrySummary telemetry={day.telemetry} />
            </AsyncBoundary>
            <div className="grid gap-4 lg:grid-cols-2">
              <AsyncBoundary>
                <TrainingSummary sessions={day.training} />
              </AsyncBoundary>
              <AsyncBoundary>
                <NutritionSummary totals={day.nutrition_totals} meals={day.meals} />
              </AsyncBoundary>
            </div>
            <AsyncBoundary>
              <RecommendationsSummary items={day.recommendations} />
            </AsyncBoundary>
          </div>
        )}
      </QueryState>
    </div>
  );
}
