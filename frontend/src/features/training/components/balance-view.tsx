"use client";

import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";

import { QueryState } from "@/components/async/query-state";
import { Skeleton } from "@/components/async/skeleton";
import { GroupedBars } from "@/components/charts/grouped-bars";
import { SectionCard } from "@/components/ui/section-card";
import { Segmented } from "@/components/ui/segmented";
import { StatCard } from "@/components/ui/stat-card";
import type { TrainingStats } from "@/lib/gateway/types";
import { formatISODate, shiftISODate, todayISODate } from "@/lib/time";

import { useTrainingStats } from "../hooks";

const RANGES = [
  { value: "4", label: "4w" },
  { value: "8", label: "8w" },
  { value: "12", label: "12w" },
] as const;

const prettyMuscle = (m: string) => m.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

/** Sets/week band colour: under target (amber), in 10–20 (green), over (red = junk volume). */
function bandColor(sets: number): string {
  if (sets < 10) return "var(--warning)";
  if (sets > 20) return "var(--destructive)";
  return "var(--success)";
}

function ratio(n: number | null): string {
  return n == null ? "—" : `${n.toFixed(2)} : 1`;
}

/** avg sets/week per muscle = total credited sets / number of weeks in range. */
function weeklyAvg(stats: TrainingStats) {
  const weeks = new Set(stats.weekly_sets_per_muscle.map((w) => w.week)).size || 1;
  const byMuscle = new Map<string, number>();
  for (const w of stats.weekly_sets_per_muscle) {
    byMuscle.set(w.muscle, (byMuscle.get(w.muscle) ?? 0) + w.sets);
  }
  return [...byMuscle.entries()]
    .map(([muscle, total]) => ({ muscle: prettyMuscle(muscle), sets: +(total / weeks).toFixed(1) }))
    .sort((a, b) => b.sets - a.sets);
}

export function BalanceView() {
  const [weeks, setWeeks] = useState("8");
  const { from, to } = useMemo(
    () => ({ from: shiftISODate(todayISODate(), -Number(weeks) * 7), to: todayISODate() }),
    [weeks],
  );
  const query = useTrainingStats(from, to);

  return (
    <div className="space-y-6">
      <Link
        href="/training"
        className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 text-sm"
      >
        <ArrowLeft className="size-4" /> Training
      </Link>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Strength balance</h1>
        <Segmented options={[...RANGES]} value={weeks} onChange={setWeeks} size="sm" />
      </div>

      <QueryState query={query} loading={<Skeleton className="h-96 w-full" />}>
        {(stats) => {
          const sets = weeklyAvg(stats);
          const volume = stats.volume_load_per_muscle
            .map((v) => ({
              muscle: prettyMuscle(v.muscle),
              volume_load: Math.round(v.volume_load),
            }))
            .sort((a, b) => b.volume_load - a.volume_load);
          const perExercise = [...stats.per_exercise].sort(
            (a, b) => (b.best_e1rm ?? 0) - (a.best_e1rm ?? 0),
          );

          return (
            <div className="space-y-4">
              <SectionCard title="Weekly volume by muscle">
                <p className="text-muted-foreground mb-2 text-xs">
                  Avg sets / week over {formatISODate(stats.from, "MMM d")}–
                  {formatISODate(stats.to, "MMM d")} vs the 10–20 target band.
                </p>
                <GroupedBars
                  data={sets}
                  xKey="muscle"
                  bars={[{ key: "sets", label: "Sets/wk" }]}
                  targetBand={{ from: 10, to: 20 }}
                  colorFor={(row) => bandColor(row.sets)}
                />
              </SectionCard>

              <div className="grid grid-cols-2 gap-3">
                <StatCard
                  label="Push : Pull"
                  value={ratio(stats.push_pull_ratio)}
                  hint="balanced ≈ 1:1"
                />
                <StatCard
                  label="Upper : Lower"
                  value={ratio(stats.upper_lower_ratio)}
                  hint="balanced ≈ 1:1"
                />
              </div>

              <SectionCard title="Volume load by muscle">
                <GroupedBars
                  data={volume}
                  xKey="muscle"
                  bars={[{ key: "volume_load", label: "Σ reps × kg" }]}
                />
              </SectionCard>

              <SectionCard title="Per exercise">
                {perExercise.length === 0 ? (
                  <p className="text-muted-foreground text-sm">No sets logged in this range.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-muted-foreground text-left text-xs">
                          <th className="py-1.5 font-medium">Exercise</th>
                          <th className="py-1.5 text-right font-medium">Sets</th>
                          <th className="py-1.5 text-right font-medium">Top</th>
                          <th className="py-1.5 text-right font-medium">e1RM</th>
                          <th className="py-1.5 text-right font-medium">PR</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {perExercise.map((e) => (
                          <tr key={e.slug ?? e.exercise}>
                            <td className="py-1.5 capitalize">{e.exercise}</td>
                            <td className="py-1.5 text-right tabular-nums">{e.sets}</td>
                            <td className="py-1.5 text-right tabular-nums">
                              {e.top_weight_kg != null ? `${e.top_weight_kg} kg` : "—"}
                            </td>
                            <td className="py-1.5 text-right tabular-nums">
                              {e.best_e1rm != null ? `${e.best_e1rm} kg` : "—"}
                            </td>
                            <td className="text-muted-foreground py-1.5 text-right text-xs">
                              {e.best_e1rm_date ? formatISODate(e.best_e1rm_date, "MMM d") : "—"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </SectionCard>

              {stats.unresolved_exercises.length ? (
                <p className="text-muted-foreground text-xs">
                  Not in the catalog (excluded from muscle stats):{" "}
                  {stats.unresolved_exercises.join(", ")}. Add them via the exercise picker.
                </p>
              ) : null}
            </div>
          );
        }}
      </QueryState>
    </div>
  );
}
