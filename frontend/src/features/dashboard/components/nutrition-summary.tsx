import { UtensilsCrossed } from "lucide-react";

import { EmptyState } from "@/components/async/empty-state";
import { Badge } from "@/components/ui/badge";
import { MetricGrid } from "@/components/ui/metric-grid";
import { SectionCard } from "@/components/ui/section-card";
import { StatCard } from "@/components/ui/stat-card";
import type { Meal, Totals } from "@/lib/gateway/types";
import { formatInstant } from "@/lib/time";

const round = (n: number) => Math.round(n).toLocaleString();

function mealKcal(meal: Meal): number {
  return meal.items.reduce((sum, it) => sum + (it.kcal ?? 0), 0);
}

/** Day nutrition: macro totals + the meals behind them. Empty is a valid state. */
export function NutritionSummary({ totals, meals }: { totals: Totals; meals: Meal[] }) {
  return (
    <SectionCard title="Nutrition" icon={<UtensilsCrossed className="size-4" />}>
      <div className="space-y-3">
        <MetricGrid className="sm:grid-cols-4">
          <StatCard label="Calories" value={totals.kcal} unit="kcal" format={round} />
          <StatCard label="Protein" value={totals.protein_g} unit="g" format={round} />
          <StatCard label="Carbs" value={totals.carbs_g} unit="g" format={round} />
          <StatCard label="Fat" value={totals.fat_g} unit="g" format={round} />
        </MetricGrid>

        {meals.length === 0 ? (
          <EmptyState
            title="No meals logged"
            description="Log a meal to see it here."
            className="border-0"
          />
        ) : (
          <ul className="divide-y">
            {meals.map((meal) => {
              const estimated = meal.items.some((it) => it.estimated);
              return (
                <li key={meal.id} className="flex items-center gap-3 py-2 first:pt-0 last:pb-0">
                  <div className="min-w-0 flex-1">
                    <p className="flex items-center gap-2 truncate text-sm">
                      {meal.name || "Meal"}
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
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </SectionCard>
  );
}
