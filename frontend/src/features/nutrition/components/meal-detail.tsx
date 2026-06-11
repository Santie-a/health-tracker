"use client";

import { ArrowLeft, Camera, Image as ImageIcon } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { QueryState } from "@/components/async/query-state";
import { Skeleton } from "@/components/async/skeleton";
import { Badge } from "@/components/ui/badge";
import { MetricGrid } from "@/components/ui/metric-grid";
import { SectionCard } from "@/components/ui/section-card";
import { StatCard } from "@/components/ui/stat-card";
import type { Meal } from "@/lib/gateway/types";
import { formatInstant } from "@/lib/time";

import { useMeal } from "../hooks";
import { AddItemForm } from "./add-item-form";
import { EditMealDialog } from "./edit-meal-dialog";
import { MealItemRow } from "./meal-item-row";

const round = (n: number) => Math.round(n).toLocaleString();

function mealTotals(meal: Meal) {
  return meal.items.reduce(
    (t, it) => ({
      kcal: t.kcal + (it.kcal ?? 0),
      protein_g: t.protein_g + (it.protein_g ?? 0),
      carbs_g: t.carbs_g + (it.carbs_g ?? 0),
      fat_g: t.fat_g + (it.fat_g ?? 0),
    }),
    { kcal: 0, protein_g: 0, carbs_g: 0, fat_g: 0 },
  );
}

export function MealDetail({ id }: { id: number }) {
  const query = useMeal(id);
  const degraded = useSearchParams().get("degraded") === "1";

  return (
    <div className="space-y-4">
      <Link
        href="/nutrition"
        className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 text-sm"
      >
        <ArrowLeft className="size-4" /> Nutrition
      </Link>

      {degraded ? (
        <div className="border-warning/40 bg-warning/10 flex items-start gap-2 rounded-lg border p-3 text-sm">
          <Camera className="text-warning mt-0.5 size-4 shrink-0" />
          <p>
            The photo service is offline, so nothing was detected. Add items manually below —
            everything else works as normal.
          </p>
        </div>
      ) : null}

      <QueryState query={query} loading={<Skeleton className="h-64 w-full" />}>
        {(meal) => {
          const totals = mealTotals(meal);
          return (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <h1 className="text-lg font-semibold tracking-tight">{meal.name || "Meal"}</h1>
                <Badge
                  variant={meal.source === "image" ? "info" : "default"}
                  className="capitalize"
                >
                  {meal.source === "image" ? <ImageIcon className="size-3" /> : null}
                  {meal.source}
                </Badge>
                <span className="text-muted-foreground text-sm">
                  {formatInstant(meal.ts, "EEE, MMM d · h:mm a")}
                </span>
                <div className="ml-auto">
                  <EditMealDialog meal={meal} />
                </div>
              </div>

              <MetricGrid className="sm:grid-cols-4">
                <StatCard label="Calories" value={totals.kcal} unit="kcal" format={round} />
                <StatCard label="Protein" value={totals.protein_g} unit="g" format={round} />
                <StatCard label="Carbs" value={totals.carbs_g} unit="g" format={round} />
                <StatCard label="Fat" value={totals.fat_g} unit="g" format={round} />
              </MetricGrid>

              <SectionCard title="Items">
                {meal.items.length === 0 ? (
                  <p className="text-muted-foreground text-sm">No items yet — add one below.</p>
                ) : (
                  <ul className="divide-y">
                    {meal.items.map((it) => (
                      <MealItemRow key={it.id} mealId={id} item={it} />
                    ))}
                  </ul>
                )}
              </SectionCard>

              <AddItemForm mealId={id} />
            </div>
          );
        }}
      </QueryState>
    </div>
  );
}
