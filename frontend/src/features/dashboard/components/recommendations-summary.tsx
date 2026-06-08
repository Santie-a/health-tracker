import { Sparkles } from "lucide-react";

import { EmptyState } from "@/components/async/empty-state";
import { Badge, type BadgeProps } from "@/components/ui/badge";
import { SectionCard } from "@/components/ui/section-card";
import type { RecommendationItem } from "@/lib/gateway/types";

/** Map a free-form severity string to a badge variant. */
function severityVariant(severity: string): BadgeProps["variant"] {
  const s = severity.toLowerCase();
  if (s === "high" || s === "critical" || s === "alert") return "destructive";
  if (s === "warning" || s === "warn" || s === "medium") return "warning";
  if (s === "good" || s === "success") return "success";
  return "info";
}

/** The day's recommendations. Thumbs-up/down feedback lands in Phase 6. */
export function RecommendationsSummary({ items }: { items: RecommendationItem[] }) {
  return (
    <SectionCard title="Advice" icon={<Sparkles className="size-4" />}>
      {items.length === 0 ? (
        <EmptyState
          title="No recommendations"
          description="Not enough data for this day, or nothing to flag."
          className="border-0"
        />
      ) : (
        <ul className="space-y-3">
          {items.map((rec) => (
            <li key={rec.code} className="rounded-lg border p-3">
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm font-medium">{rec.title}</p>
                <Badge variant={severityVariant(rec.severity)} className="shrink-0 capitalize">
                  {rec.severity}
                </Badge>
              </div>
              <p className="text-muted-foreground mt-1 text-sm">{rec.detail}</p>
              {rec.signals.length ? (
                <p className="text-muted-foreground mt-1.5 text-xs">{rec.signals.join(" · ")}</p>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </SectionCard>
  );
}
