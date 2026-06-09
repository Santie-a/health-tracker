import { Badge, type BadgeProps } from "@/components/ui/badge";
import type { RecommendationItem } from "@/lib/gateway/types";

/** Map a free-form severity string to a badge variant. */
export function severityVariant(severity: string): BadgeProps["variant"] {
  const s = severity.toLowerCase();
  if (s === "high" || s === "critical" || s === "alert") return "destructive";
  if (s === "warning" || s === "warn" || s === "medium") return "warning";
  if (s === "good" || s === "success") return "success";
  return "info";
}

/** One recommendation: title + severity, detail, category, and the signals behind it. */
export function RecommendationCard({ rec }: { rec: RecommendationItem }) {
  return (
    <div className="rounded-lg border p-3">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm font-medium">{rec.title}</p>
        <Badge variant={severityVariant(rec.severity)} className="shrink-0 capitalize">
          {rec.severity}
        </Badge>
      </div>
      <p className="text-muted-foreground mt-1 text-sm">{rec.detail}</p>
      <p className="text-muted-foreground mt-1.5 text-xs">
        {[rec.category, ...rec.signals].filter(Boolean).join(" · ")}
      </p>
    </div>
  );
}
