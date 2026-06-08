import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query/keys";

import { getDashboard, getGatewayHealth } from "./api";

/** Polls gateway connectivity periodically so the badge reflects the live state. */
export function useGatewayHealth() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: getGatewayHealth,
    refetchInterval: 30_000,
  });
}

/** The aggregated day view for a given calendar date. */
export function useDashboard(date: string) {
  return useQuery({
    queryKey: queryKeys.dashboard(date),
    queryFn: () => getDashboard(date),
  });
}
