"use client";

import { Skeleton } from "@/components/async/skeleton";
import { QueryState } from "@/components/async/query-state";
import { cn } from "@/lib/utils";

import { useGatewayHealth } from "../hooks";

const DOT: Record<string, string> = {
  ready: "bg-success",
  degraded: "bg-warning",
  unreachable: "bg-destructive",
};

/**
 * Live gateway connection badge. Demonstrates the full data path
 * (component → hook → BFF → gateway) and renders connection state as data — degraded
 * and unreachable are shown, not thrown.
 */
export function GatewayStatus() {
  const query = useGatewayHealth();

  return (
    <div className="rounded-lg border p-4">
      <QueryState query={query} loading={<Skeleton className="h-6 w-48" />}>
        {(health) => (
          <div className="flex items-center gap-3">
            <span className={cn("size-2.5 rounded-full", DOT[health.gateway] ?? "bg-muted")} />
            <div className="text-sm">
              <span className="font-medium capitalize">Gateway {health.gateway}</span>
              {health.gateway === "ready" && (
                <span className="text-muted-foreground">
                  {" "}
                  · database {health.database ? "connected" : "down"}
                </span>
              )}
              {health.reason && <span className="text-muted-foreground"> · {health.reason}</span>}
            </div>
          </div>
        )}
      </QueryState>
    </div>
  );
}
