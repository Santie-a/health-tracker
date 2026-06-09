import type { BodyCompositionPoint, DailyRollup, SleepNight } from "@/lib/gateway/types";
import { apiGet } from "@/lib/query/fetcher";

export function getDailyMetric(metric: string, from: string, to: string): Promise<DailyRollup[]> {
  return apiGet<DailyRollup[]>("/api/telemetry/daily", { metric, from, to });
}

export function getSleepSeries(from: string, to: string): Promise<SleepNight[]> {
  return apiGet<SleepNight[]>("/api/telemetry/sleep", { from, to });
}

export function getBodyComposition(from: string, to: string): Promise<BodyCompositionPoint[]> {
  return apiGet<BodyCompositionPoint[]>("/api/body-composition", { from, to });
}
