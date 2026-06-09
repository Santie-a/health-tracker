"use client";

import { BarChart3 } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { EmptyState } from "@/components/async/empty-state";
import { QueryState } from "@/components/async/query-state";
import { Skeleton } from "@/components/async/skeleton";
import { buttonVariants } from "@/components/ui/button";
import { Segmented } from "@/components/ui/segmented";
import { cn } from "@/lib/utils";

import { useTrainingSessions } from "../hooks";
import { NewSessionDialog } from "./new-session-dialog";
import { TrainingList } from "./training-list";

type Filter = "all" | "gym" | "swim";

export function TrainingView() {
  const [filter, setFilter] = useState<Filter>("all");
  const query = useTrainingSessions(filter === "all" ? {} : { type: filter });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Training</h1>
        <div className="flex items-center gap-2">
          <Link
            href="/training/balance"
            className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
          >
            <BarChart3 /> Balance
          </Link>
          <NewSessionDialog />
        </div>
      </div>

      <Segmented
        options={[
          { value: "all", label: "All" },
          { value: "gym", label: "Gym" },
          { value: "swim", label: "Swim" },
        ]}
        value={filter}
        onChange={setFilter}
        size="sm"
      />

      <QueryState
        query={query}
        loading={<Skeleton className="h-48 w-full" />}
        isEmpty={(sessions) => sessions.length === 0}
        empty={
          <EmptyState
            title="No sessions yet"
            description="Log your first gym or swim session to see it here."
          />
        }
      >
        {(sessions) => <TrainingList sessions={sessions} />}
      </QueryState>
    </div>
  );
}
