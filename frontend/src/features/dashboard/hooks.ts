import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query/keys";

import { getDashboard } from "./api";

/** The aggregated day view for a given calendar date. */
export function useDashboard(date: string) {
  return useQuery({
    queryKey: queryKeys.dashboard(date),
    queryFn: () => getDashboard(date),
  });
}
