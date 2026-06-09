import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query/keys";

import { getRecommendations } from "./api";

/** The day's recommendations (the gateway generates + stores them on first request). */
export function useRecommendations(date: string) {
  return useQuery({
    queryKey: queryKeys.recommendations(date),
    queryFn: () => getRecommendations(date),
  });
}
