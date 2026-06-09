import type { RecommendationsOut } from "@/lib/gateway/types";
import { apiGet, apiSend } from "@/lib/query/fetcher";

export function getRecommendations(date: string): Promise<RecommendationsOut> {
  return apiGet<RecommendationsOut>("/api/recommendations", { date });
}

/** Force a regenerate (the daily-pass trigger). */
export function runRecommendations(date: string): Promise<RecommendationsOut> {
  return apiSend<RecommendationsOut>("/api/recommendations/run", {
    method: "POST",
    query: { date },
  });
}

/** Day-level feedback ("up" | "down"). 204 on success; 404 if none stored yet. */
export function submitFeedback(date: string, feedback: string): Promise<void> {
  return apiSend<void>("/api/recommendations/feedback", { json: { date, feedback } });
}
