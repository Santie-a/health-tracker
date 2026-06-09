import type {
  Exercise,
  ExerciseIn,
  TrainingSession,
  TrainingSessionIn,
  TrainingSetIn,
} from "@/lib/gateway/types";
import { apiGet, apiSend } from "@/lib/query/fetcher";

export type SessionFilters = {
  type?: string;
  from?: string;
  to?: string;
  limit?: number;
};

export function listTrainingSessions(filters: SessionFilters = {}): Promise<TrainingSession[]> {
  return apiGet<TrainingSession[]>("/api/training", { ...filters });
}

export function getTrainingSession(id: number): Promise<TrainingSession> {
  return apiGet<TrainingSession>(`/api/training/${id}`);
}

export function createTrainingSession(body: TrainingSessionIn): Promise<TrainingSession> {
  return apiSend<TrainingSession>("/api/training", { json: body });
}

export function addSets(id: number, sets: TrainingSetIn[]): Promise<TrainingSession> {
  return apiSend<TrainingSession>(`/api/training/${id}/sets`, { json: { sets } });
}

export type ExerciseFilters = {
  q?: string;
  muscle?: string;
  category?: string;
  limit?: number;
};

export function searchExercises(filters: ExerciseFilters = {}): Promise<Exercise[]> {
  return apiGet<Exercise[]>("/api/exercises", { ...filters });
}

export function createExercise(body: ExerciseIn): Promise<Exercise> {
  return apiSend<Exercise>("/api/exercises", { json: body });
}
