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
