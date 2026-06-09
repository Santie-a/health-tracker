import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query/keys";

import { getDayNutrition, getMeal, recentFoods, searchFoods } from "./api";

export function useDayNutrition(date: string) {
  return useQuery({
    queryKey: queryKeys.nutrition.day(date),
    queryFn: () => getDayNutrition(date),
  });
}

export function useMeal(id: number) {
  return useQuery({
    queryKey: queryKeys.nutrition.meal(id),
    queryFn: () => getMeal(id),
    enabled: Number.isInteger(id),
  });
}

export function useFoodSearch(q: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.foods.search(q),
    queryFn: () => searchFoods(q),
    enabled,
    placeholderData: keepPreviousData,
  });
}

export function useRecentFoods() {
  return useQuery({
    queryKey: queryKeys.foods.recent,
    queryFn: recentFoods,
  });
}
