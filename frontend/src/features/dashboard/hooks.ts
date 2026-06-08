import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query/keys";

import { getGatewayHealth } from "./api";

/** Polls gateway connectivity periodically so the badge reflects the live state. */
export function useGatewayHealth() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: getGatewayHealth,
    refetchInterval: 30_000,
  });
}
