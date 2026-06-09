import { Dumbbell, Waves } from "lucide-react";

import { EmptyState } from "@/components/async/empty-state";
import { Badge } from "@/components/ui/badge";
import { SectionCard } from "@/components/ui/section-card";
import type { TrainingSession } from "@/lib/gateway/types";
import { formatInstant } from "@/lib/time";

function sessionLine(s: TrainingSession): string {
  const parts: string[] = [];
  if (s.type === "swim" && s.distance_m != null) parts.push(`${s.distance_m} m`);
  if (s.duration_min != null) parts.push(`${s.duration_min} min`);
  if (s.load != null) parts.push(`load ${Math.round(s.load)}`);
  else if (s.rpe != null) parts.push(`RPE ${s.rpe}`);
  const working = s.sets.filter((set) => !set.is_warmup).length;
  if (working) parts.push(`${working} ${working === 1 ? "set" : "sets"}`);
  return parts.join(" · ");
}

/** The day's training sessions (manual + watch-imported). Empty is a valid state. */
export function TrainingSummary({ sessions }: { sessions: TrainingSession[] }) {
  return (
    <SectionCard title="Training" icon={<Dumbbell className="size-4" />}>
      {sessions.length === 0 ? (
        <EmptyState
          title="No training logged"
          description="Nothing recorded for this day."
          className="border-0"
        />
      ) : (
        <ul className="divide-y">
          {sessions.map((s) => (
            <li key={s.id} className="flex items-center gap-3 py-2 first:pt-0 last:pb-0">
              <Badge variant={s.type === "swim" ? "info" : "default"} className="capitalize">
                {s.type === "swim" ? <Waves className="size-3" /> : <Dumbbell className="size-3" />}
                {s.type}
              </Badge>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm">{sessionLine(s) || "Session"}</p>
                {s.notes ? (
                  <p className="text-muted-foreground truncate text-xs">{s.notes}</p>
                ) : null}
              </div>
              <span className="text-muted-foreground shrink-0 text-xs">
                {formatInstant(s.ts, "h:mm a")}
              </span>
            </li>
          ))}
        </ul>
      )}
    </SectionCard>
  );
}
