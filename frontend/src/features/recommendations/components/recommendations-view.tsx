"use client";

import { RefreshCw, ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { EmptyState } from "@/components/async/empty-state";
import { QueryState } from "@/components/async/query-state";
import { Skeleton } from "@/components/async/skeleton";
import { DateNav } from "@/components/date-nav";
import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/query/fetcher";
import { queryKeys } from "@/lib/query/keys";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";
import { formatISODate, todayISODate } from "@/lib/time";
import { cn } from "@/lib/utils";

import { runRecommendations, submitFeedback } from "../api";
import { useRecommendations } from "../hooks";
import { RecommendationCard } from "./recommendation-card";

export function RecommendationsView() {
  const [date, setDate] = useState(todayISODate);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const query = useRecommendations(date);

  function changeDate(d: string) {
    setDate(d);
    setFeedback(null); // feedback is day-scoped; reset when the day changes
  }

  const rerun = useGatewayMutation({
    mutationFn: () => runRecommendations(date),
    update: (qc, data) => qc.setQueryData(queryKeys.recommendations(date), data),
    invalidate: [["dashboard"]],
    successMessage: "Recommendations regenerated",
  });

  async function sendFeedback(value: string) {
    setFeedback(value); // optimistic highlight
    setSending(true);
    try {
      try {
        await submitFeedback(date, value);
      } catch (err) {
        // 404 = nothing stored for this day yet → generate, then retry once.
        if (err instanceof ApiError && err.status === 404) {
          await runRecommendations(date);
          await submitFeedback(date, value);
        } else {
          throw err;
        }
      }
      toast.success("Thanks for the feedback");
    } catch (err) {
      setFeedback(null);
      toast.error(err instanceof ApiError ? err.friendly : "Couldn't save feedback");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Advice</h1>
        <div className="flex items-center gap-2">
          <DateNav date={date} onChange={changeDate} />
          <Button
            variant="outline"
            size="icon"
            aria-label="Regenerate"
            loading={rerun.isPending}
            onClick={() => rerun.mutate(undefined)}
          >
            <RefreshCw />
          </Button>
        </div>
      </div>

      <QueryState query={query} loading={<Skeleton className="h-48 w-full" />}>
        {(data) =>
          data.recommendations.length === 0 ? (
            <EmptyState
              title="No recommendations"
              description="Not enough data for this day, or nothing to flag. Log training, meals, or sync your watch."
            />
          ) : (
            <div className="space-y-4">
              <p className="text-muted-foreground text-sm">
                {formatISODate(data.date, "EEEE, MMM d")} · {data.recommendations.length} item
                {data.recommendations.length === 1 ? "" : "s"}
              </p>
              <ul className="space-y-3">
                {data.recommendations.map((rec) => (
                  <li key={rec.code}>
                    <RecommendationCard rec={rec} />
                  </li>
                ))}
              </ul>

              <div className="flex items-center gap-3 border-t pt-4">
                <span className="text-muted-foreground text-sm">Was this helpful?</span>
                <Button
                  variant={feedback === "up" ? "default" : "outline"}
                  size="sm"
                  disabled={sending}
                  onClick={() => sendFeedback("up")}
                >
                  <ThumbsUp /> Yes
                </Button>
                <Button
                  variant={feedback === "down" ? "destructive" : "outline"}
                  size="sm"
                  disabled={sending}
                  onClick={() => sendFeedback("down")}
                >
                  <ThumbsDown className={cn(feedback === "down" && "fill-current")} /> No
                </Button>
              </div>
            </div>
          )
        }
      </QueryState>
    </div>
  );
}
