import type {
  Exercise,
  ExerciseIn,
  ExerciseUpdate,
  TrainingSession,
  TrainingSessionIn,
  TrainingSessionUpdate,
  TrainingSetIn,
  TrainingSetUpdate,
  TrainingStats,
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

export function updateTrainingSession(
  id: number,
  body: TrainingSessionUpdate,
): Promise<TrainingSession> {
  return apiSend<TrainingSession>(`/api/training/${id}`, { method: "PATCH", json: body });
}

export function deleteTrainingSession(id: number): Promise<void> {
  return apiSend<void>(`/api/training/${id}`, { method: "DELETE" });
}

/** Edit one set; the gateway returns the updated session. */
export function updateSet(
  id: number,
  setId: number,
  body: TrainingSetUpdate,
): Promise<TrainingSession> {
  return apiSend<TrainingSession>(`/api/training/${id}/sets/${setId}`, {
    method: "PATCH",
    json: body,
  });
}

/** Remove one set; the gateway returns the updated session. */
export function deleteSet(id: number, setId: number): Promise<TrainingSession> {
  return apiSend<TrainingSession>(`/api/training/${id}/sets/${setId}`, { method: "DELETE" });
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

export function updateExercise(id: number, body: ExerciseUpdate): Promise<Exercise> {
  return apiSend<Exercise>(`/api/exercises/${id}`, { method: "PATCH", json: body });
}

/** Returns the action the gateway took: hard `deleted` or soft `deactivated`. */
export function deleteExercise(id: number): Promise<{ action: "deleted" | "deactivated" }> {
  return apiSend<{ action: "deleted" | "deactivated" }>(`/api/exercises/${id}`, {
    method: "DELETE",
  });
}

export function getTrainingStats(from?: string, to?: string): Promise<TrainingStats> {
  return apiGet<TrainingStats>("/api/training/stats", { from, to });
}
