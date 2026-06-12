import { CalendarCheck, Moon, TrendingUp } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { GoalWithProgress } from "@/lib/gateway/types";
import { formatISODate } from "@/lib/time";

import {
  formatMetric,
  formatRate,
  GOAL_TYPE_LABEL,
  metricLabel,
  PROGRESS_META,
  progressColor,
} from "../meta";
import { EditGoalDialog } from "./edit-goal-dialog";
import { ProgressRing } from "./progress-ring";

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-muted-foreground text-xs">{label}</dt>
      <dd className="text-sm font-medium tabular-nums">{value}</dd>
    </div>
  );
}

/** One active goal: progress ring + the trend vs target, with inline edit. */
export function GoalCard({ goal }: { goal: GoalWithProgress }) {
  const p = goal.progress;
  const meta = PROGRESS_META[p.status];
  const color = progressColor(p.status);
  const hasPct = p.pct_complete != null;
  const Icon = goal.category === "sleep" ? Moon : TrendingUp;

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            <Icon className="text-muted-foreground size-4" />
            <div>
              <p className="font-semibold">{GOAL_TYPE_LABEL[goal.type]}</p>
              <p className="text-muted-foreground text-xs">{metricLabel(goal.metric)}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={meta.variant}>{meta.label}</Badge>
            <EditGoalDialog goal={goal} />
          </div>
        </div>

        <div className="mt-4 flex items-center gap-5">
          <ProgressRing
            value={p.pct_complete ?? null}
            color={color}
            label={
              hasPct
                ? `${Math.round((p.pct_complete ?? 0) * 100)}%`
                : formatMetric(p.current_value, goal.metric)
            }
            sublabel={hasPct ? "to target" : metricLabel(goal.metric)}
          />

          <dl className="grid flex-1 grid-cols-2 gap-x-4 gap-y-3">
            <Stat label="Current" value={formatMetric(p.current_value, goal.metric)} />
            <Stat label="Target" value={formatMetric(p.target_value, goal.metric)} />
            <Stat label="Pace" value={formatRate(p.actual_rate_per_week, goal.metric)} />
            <Stat label="Target pace" value={formatRate(p.target_rate_per_week, goal.metric)} />
          </dl>
        </div>

        <p className="text-muted-foreground mt-4 text-sm">{p.summary}</p>

        <div className="text-muted-foreground mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs">
          {p.projected_date ? (
            <span className="inline-flex items-center gap-1">
              <CalendarCheck className="size-3.5" />
              Projected {formatISODate(p.projected_date, "MMM d, yyyy")}
            </span>
          ) : null}
          <span>
            {p.n_readings} reading{p.n_readings === 1 ? "" : "s"}
          </span>
          <span>day {p.days_elapsed}</span>
        </div>
      </CardContent>
    </Card>
  );
}
