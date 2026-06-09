import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query/keys";

import { getBodyComposition, getDailyMetric, getSleepSeries } from "./api";

export function useDailyMetric(metric: string, from: string, to: string) {
  return useQuery({
    queryKey: queryKeys.telemetry.daily(metric, from, to),
    queryFn: () => getDailyMetric(metric, from, to),
  });
}

export function useSleepSeries(from: string, to: string) {
  return useQuery({
    queryKey: queryKeys.telemetry.sleep(from, to),
    queryFn: () => getSleepSeries(from, to),
  });
}

export function useBodyComposition(from: string, to: string) {
  return useQuery({
    queryKey: queryKeys.telemetry.bodyComposition(from, to),
    queryFn: () => getBodyComposition(from, to),
  });
}
