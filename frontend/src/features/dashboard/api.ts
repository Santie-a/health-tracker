import type { Dashboard } from "@/lib/gateway/types";
import { apiGet } from "@/lib/query/fetcher";

/** The aggregated day view for a calendar date (YYYY-MM-DD, local). */
export function getDashboard(date: string): Promise<Dashboard> {
  return apiGet<Dashboard>("/api/dashboard", { date });
}
