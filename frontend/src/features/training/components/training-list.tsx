import { ChevronRight, Dumbbell, Waves } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import type { TrainingSession } from "@/lib/gateway/types";
import { formatInstant } from "@/lib/time";

function summary(s: TrainingSession): string {
  const parts: string[] = [];
  if (s.type === "swim" && s.distance_m != null) parts.push(`${s.distance_m} m`);
  if (s.duration_min != null) parts.push(`${s.duration_min} min`);
  if (s.load != null) parts.push(`load ${Math.round(s.load)}`);
  else if (s.rpe != null) parts.push(`RPE ${s.rpe}`);
  const working = s.sets.filter((set) => !set.is_warmup).length;
  if (working) parts.push(`${working} ${working === 1 ? "set" : "sets"}`);
  return parts.join(" · ");
}

/** Tappable list of sessions, each linking to its detail / set logger. */
export function TrainingList({ sessions }: { sessions: TrainingSession[] }) {
  return (
    <ul className="divide-y rounded-xl border">
      {sessions.map((s) => (
        <li key={s.id}>
          <Link
            href={`/training/${s.id}`}
            className="hover:bg-accent/50 flex items-center gap-3 p-3 transition-colors"
          >
            <Badge variant={s.type === "swim" ? "info" : "default"} className="capitalize">
              {s.type === "swim" ? <Waves className="size-3" /> : <Dumbbell className="size-3" />}
              {s.type}
            </Badge>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm">{summary(s) || "Session"}</p>
              <p className="text-muted-foreground text-xs">
                {formatInstant(s.ts, "EEE, MMM d · h:mm a")}
                {s.source !== "manual" ? " · watch" : ""}
              </p>
            </div>
            <ChevronRight className="text-muted-foreground size-4 shrink-0" />
          </Link>
        </li>
      ))}
    </ul>
  );
}
