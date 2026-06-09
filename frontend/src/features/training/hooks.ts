import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query/keys";

import {
  getTrainingSession,
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

/** Exercise catalog search. `keepPreviousData` avoids flicker while typing. */
export function useExerciseSearch(filters: ExerciseFilters, enabled = true) {
  return useQuery({
    queryKey: queryKeys.exercises(filters),
    queryFn: () => searchExercises(filters),
    enabled,
    placeholderData: keepPreviousData,
  });
}
