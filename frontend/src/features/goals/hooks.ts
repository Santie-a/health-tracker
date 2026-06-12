import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query/keys";

import { getActiveGoals, listGoals } from "./api";

/** The current active goal(s) with progress (body + sleep). */
export function useActiveGoals() {
  return useQuery({
    queryKey: queryKeys.goals.active,
    queryFn: getActiveGoals,
  });
}

/** All goals, optionally filtered by status — used for the "past goals" history. */
export function useGoals(status?: string) {
  return useQuery({
    queryKey: queryKeys.goals.list(status),
    queryFn: () => listGoals(status),
  });
}
