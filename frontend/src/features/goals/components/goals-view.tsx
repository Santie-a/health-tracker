"use client";

import { Target } from "lucide-react";

import { EmptyState } from "@/components/async/empty-state";
import { QueryState } from "@/components/async/query-state";
import { Skeleton } from "@/components/async/skeleton";
import { Badge } from "@/components/ui/badge";
import type { Goal } from "@/lib/gateway/types";
import { formatISODate } from "@/lib/time";

import { useActiveGoals, useGoals } from "../hooks";
import { GOAL_TYPE_LABEL } from "../meta";
import { EditGoalDialog } from "./edit-goal-dialog";
import { GoalCard } from "./goal-card";
import { NewGoalDialog } from "./new-goal-dialog";

function PastGoalRow({ goal }: { goal: Goal }) {
  return (
    <li className="flex items-center justify-between gap-3 rounded-lg border px-3 py-2">
      <div className="min-w-0">
        <p className="truncate text-sm font-medium">{GOAL_TYPE_LABEL[goal.type]}</p>
        <p className="text-muted-foreground text-xs">
          {formatISODate(goal.start_date, "MMM d, yyyy")}
          {goal.target_date ? ` → ${formatISODate(goal.target_date, "MMM d, yyyy")}` : ""}
        </p>
      </div>
      <div className="flex items-center gap-2">
        <Badge variant={goal.status === "achieved" ? "success" : "default"} className="capitalize">
          {goal.status}
        </Badge>
        <EditGoalDialog goal={goal} />
      </div>
    </li>
  );
}

export function GoalsView() {
  const active = useActiveGoals();
  const all = useGoals();

  const past = (all.data ?? []).filter((g) => g.status !== "active");

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Goals</h1>
        <NewGoalDialog />
      </div>

      <section className="space-y-4">
        <QueryState
          query={active}
          loading={
            <div className="grid gap-4 lg:grid-cols-2">
              <Skeleton className="h-56 w-full" />
              <Skeleton className="h-56 w-full" />
            </div>
          }
          isEmpty={(data) => data.length === 0}
          empty={
            <EmptyState
              icon={<Target className="size-6" />}
              title="No active goals"
              description="Set a goal — gain muscle, gain weight, or improve sleep — and your daily advice turns directional, tracking your progress against it."
            />
          }
        >
          {(goals) => (
            <div className="grid gap-4 lg:grid-cols-2">
              {goals.map((goal) => (
                <GoalCard key={goal.id} goal={goal} />
              ))}
            </div>
          )}
        </QueryState>
      </section>

      {past.length > 0 ? (
        <section className="space-y-3">
          <h2 className="text-muted-foreground text-sm font-medium">Past goals</h2>
          <ul className="space-y-2">
            {past.map((goal) => (
              <PastGoalRow key={goal.id} goal={goal} />
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}
