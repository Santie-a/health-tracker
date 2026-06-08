import type { Dashboard } from "@/lib/gateway/types";
import { apiGet } from "@/lib/query/fetcher";

export interface GatewayHealth {
  ok: boolean;
  gateway: "ready" | "degraded" | "unreachable";
  database?: boolean | null;
  reason?: string;
}

/** Browser → BFF connectivity check (same-origin). */
export function getGatewayHealth(): Promise<GatewayHealth> {
  return apiGet<GatewayHealth>("/api/health");
}

/** The aggregated day view for a calendar date (YYYY-MM-DD, local). */
export function getDashboard(date: string): Promise<Dashboard> {
  return apiGet<Dashboard>("/api/dashboard", { date });
}
