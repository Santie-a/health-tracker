import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query/keys";

import {
  getTrainingSession,
  getTrainingStats,
  listTrainingSessions,
  searchExercises,
  type ExerciseFilters,
  type SessionFilters,
} from "./api";

export function useTrainingSessions(filters: SessionFilters = {}) {
  return useQuery({
    queryKey: queryKeys.training.list(filters),
    queryFn: () => listTrainingSessions(filters),
  });
}

export function useTrainingSession(id: number) {
  return useQuery({
    queryKey: queryKeys.training.session(id),
    queryFn: () => getTrainingSession(id),
    enabled: Number.isInteger(id),
  });
}

export function useTrainingStats(from?: string, to?: string) {
  return useQuery({
    queryKey: queryKeys.training.stats(from, to),
    queryFn: () => getTrainingStats(from, to),
  });
}

/** Exercise catalog search. `keepPreviousData` avoids flicker while typing. */
export function useExerciseSearch(filters: ExerciseFilters, enabled = true) {
  return useQuery({
    queryKey: queryKeys.exercises(filters),
    queryFn: () => searchExercises(filters),
    enabled,
    placeholderData: keepPreviousData,
  });
}
