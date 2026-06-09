"use client";

import { useQuery } from "@tanstack/react-query";
import { WifiOff } from "lucide-react";

import { apiGet } from "@/lib/query/fetcher";
import { queryKeys } from "@/lib/query/keys";

interface GatewayHealth {
  ok: boolean;
  gateway: "ready" | "degraded" | "unreachable";
  database?: boolean | null;
  reason?: string;
}

/**
 * Thin banner shown only when the gateway is unreachable or degraded. Polls the BFF
 * health route so a Pi5/PC hiccup is surfaced calmly (and disappears on recovery)
 * instead of every view erroring on its own.
 */
export function ConnectionBanner() {
  const { data } = useQuery({
    queryKey: queryKeys.health,
    queryFn: () => apiGet<GatewayHealth>("/api/health"),
    refetchInterval: 30_000,
    refetchOnWindowFocus: true,
  });

  if (!data || data.gateway === "ready") return null;

  const message =
    data.gateway === "unreachable"
      ? "Can't reach the server. Your changes may not save until it's back."
      : "The server is degraded (database unavailable). Some data may be missing.";

  return (
    <div className="bg-warning/15 text-warning flex items-center justify-center gap-2 px-4 py-1.5 text-center text-xs font-medium">
      <WifiOff className="size-3.5 shrink-0" />
      {message}
    </div>
  );
}
