import { Sparkles } from "lucide-react";

import { EmptyState } from "@/components/async/empty-state";
import { SectionCard } from "@/components/ui/section-card";
import { RecommendationCard } from "@/features/recommendations/components/recommendation-card";
import type { RecommendationItem } from "@/lib/gateway/types";

/** The day's recommendations. Thumbs-up/down feedback lives on the full Advice view. */
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
            <li key={rec.code}>
              <RecommendationCard rec={rec} />
            </li>
          ))}
        </ul>
      )}
    </SectionCard>
  );
}
