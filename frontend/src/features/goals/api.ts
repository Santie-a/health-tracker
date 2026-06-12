import type { Goal, GoalIn, GoalUpdate, GoalWithProgress } from "@/lib/gateway/types";
import { apiGet, apiSend } from "@/lib/query/fetcher";

export function listGoals(status?: string): Promise<Goal[]> {
  return apiGet<Goal[]>("/api/goals", status ? { status } : undefined);
}

/** Active goal(s) with live progress (the /goals page's primary read). */
export function getActiveGoals(): Promise<GoalWithProgress[]> {
  return apiGet<GoalWithProgress[]>("/api/goals/active");
}

export function createGoal(body: GoalIn): Promise<Goal> {
  return apiSend<Goal>("/api/goals", { json: body });
}

export function updateGoal(id: number, body: GoalUpdate): Promise<Goal> {
  return apiSend<Goal>(`/api/goals/${id}`, { method: "PATCH", json: body });
}

export function deleteGoal(id: number): Promise<void> {
  return apiSend<void>(`/api/goals/${id}`, { method: "DELETE" });
}
