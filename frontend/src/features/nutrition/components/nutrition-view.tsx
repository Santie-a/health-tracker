"use client";

import { ChevronRight, ImageIcon } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { EmptyState } from "@/components/async/empty-state";
import { QueryState } from "@/components/async/query-state";
import { Skeleton } from "@/components/async/skeleton";
import { DateNav } from "@/components/date-nav";
import { Badge } from "@/components/ui/badge";
import { MetricGrid } from "@/components/ui/metric-grid";
import { StatCard } from "@/components/ui/stat-card";
import type { Meal } from "@/lib/gateway/types";
import { formatInstant, todayISODate } from "@/lib/time";

import { useDayNutrition } from "../hooks";
import { NewMealDialog } from "./new-meal-dialog";
import { PhotoUpload } from "./photo-upload";

const round = (n: number) => Math.round(n).toLocaleString();

function mealKcal(meal: Meal): number {
  return meal.items.reduce((s, it) => s + (it.kcal ?? 0), 0);
}

export function NutritionView() {
  const [date, setDate] = useState(todayISODate);
  const query = useDayNutrition(date);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Nutrition</h1>
        <div className="flex items-center gap-2">
          <PhotoUpload />
          <NewMealDialog />
        </div>
      </div>

      <DateNav date={date} onChange={setDate} />

      <QueryState query={query} loading={<Skeleton className="h-48 w-full" />}>
        {(day) => (
          <div className="space-y-4">
            <MetricGrid className="sm:grid-cols-4">
              <StatCard label="Calories" value={day.totals.kcal} unit="kcal" format={round} />
              <StatCard label="Protein" value={day.totals.protein_g} unit="g" format={round} />
              <StatCard label="Carbs" value={day.totals.carbs_g} unit="g" format={round} />
              <StatCard label="Fat" value={day.totals.fat_g} unit="g" format={round} />
            </MetricGrid>

            {day.meals.length === 0 ? (
              <EmptyState
                title="No meals logged"
                description="Log a meal or snap a photo to start tracking this day."
              />
            ) : (
              <ul className="divide-y rounded-xl border">
                {day.meals.map((meal) => {
                  const estimated = meal.items.some((it) => it.estimated);
                  return (
                    <li key={meal.id}>
                      <Link
                        href={`/nutrition/${meal.id}`}
                        className="hover:bg-accent/50 flex items-center gap-3 p-3 transition-colors"
                      >
                        <div className="min-w-0 flex-1">
                          <p className="flex items-center gap-2 truncate text-sm font-medium">
                            {meal.name || "Meal"}
                            {meal.source === "photo" ? (
                              <ImageIcon className="text-muted-foreground size-3.5" />
                            ) : null}
                            {estimated ? <Badge variant="info">estimated</Badge> : null}
                          </p>
                          <p className="text-muted-foreground text-xs">
                            {meal.items.length} {meal.items.length === 1 ? "item" : "items"} ·{" "}
                            {formatInstant(meal.ts, "h:mm a")}
                          </p>
                        </div>
                        <span className="text-muted-foreground shrink-0 text-sm tabular-nums">
                          {round(mealKcal(meal))} kcal
                        </span>
                        <ChevronRight className="text-muted-foreground size-4 shrink-0" />
                      </Link>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        )}
      </QueryState>
    </div>
  );
}
