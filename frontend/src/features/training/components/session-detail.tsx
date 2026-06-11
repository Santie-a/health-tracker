"use client";

import { ArrowLeft, Dumbbell, Waves } from "lucide-react";
import Link from "next/link";

import { QueryState } from "@/components/async/query-state";
import { Skeleton } from "@/components/async/skeleton";
import { Badge } from "@/components/ui/badge";
import { SectionCard } from "@/components/ui/section-card";
import type { TrainingSession } from "@/lib/gateway/types";
import { formatInstant } from "@/lib/time";

import { useTrainingSession } from "../hooks";
import { AddSetForm } from "./add-set-form";
import { EditSessionDialog } from "./edit-session-dialog";
import { SetRow } from "./set-row";

function header(s: TrainingSession): string {
  const parts = [
    s.duration_min != null ? `${s.duration_min} min` : null,
    s.load != null ? `load ${Math.round(s.load)}` : null,
    s.rpe != null ? `RPE ${s.rpe}` : null,
    s.kcal != null ? `${Math.round(s.kcal)} kcal` : null,
  ].filter(Boolean);
  return parts.join(" · ");
}

export function SessionDetail({ id }: { id: number }) {
  const query = useTrainingSession(id);

  return (
    <div className="space-y-4">
      <Link
        href="/training"
        className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 text-sm"
      >
        <ArrowLeft className="size-4" /> Training
      </Link>

      <QueryState query={query} loading={<Skeleton className="h-64 w-full" />}>
        {(session) => {
          const sets = session.sets;
          const lastSet = sets.length ? sets[sets.length - 1] : undefined;
          return (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <Badge
                  variant={session.type === "swim" ? "info" : "default"}
                  className="capitalize"
                >
                  {session.type === "swim" ? (
                    <Waves className="size-3" />
                  ) : (
                    <Dumbbell className="size-3" />
                  )}
                  {session.type}
                </Badge>
                <div>
                  <h1 className="text-lg font-semibold tracking-tight">
                    {formatInstant(session.ts, "EEE, MMM d · h:mm a")}
                  </h1>
                  {header(session) ? (
                    <p className="text-muted-foreground text-sm">{header(session)}</p>
                  ) : null}
                </div>
                <div className="ml-auto">
                  <EditSessionDialog session={session} />
                </div>
              </div>
              {session.notes ? (
                <p className="bg-muted/50 rounded-md p-3 text-sm">{session.notes}</p>
              ) : null}

              <SectionCard title="Sets">
                {sets.length === 0 ? (
                  <p className="text-muted-foreground text-sm">No sets yet — add one below.</p>
                ) : (
                  <ol className="divide-y">
                    {sets.map((s, i) => (
                      <SetRow key={s.id} sessionId={id} set={s} index={i} />
                    ))}
                  </ol>
                )}
              </SectionCard>

              <AddSetForm sessionId={id} lastSet={lastSet} />
            </div>
          );
        }}
      </QueryState>
    </div>
  );
}
