import type { components } from "./types.gen";

/**
 * Friendly aliases over the generated OpenAPI schemas. Features import domain types
 * from here (not the generated file) so the indirection is in one place and the
 * generated output stays an implementation detail. Pure types — safe on the client.
 */
type S = components["schemas"];

export type Dashboard = S["DashboardOut"];
export type TelemetrySummary = S["TelemetrySummary"];
export type SleepSummary = S["SleepSummary"];
export type Totals = S["Totals"];
export type RecommendationItem = S["RecommendationItem"];

export type TrainingSession = S["TrainingSessionOut"];
export type TrainingSet = S["TrainingSetOut"];
export type TrainingSessionIn = S["TrainingSessionIn"];
export type TrainingSetIn = S["TrainingSetIn"];
export type SessionType = TrainingSessionIn["type"]; // "swim" | "gym"

export type Exercise = S["ExerciseOut"];
export type ExerciseIn = S["ExerciseIn"];
export type ExerciseCategory = NonNullable<ExerciseIn["category"]>;

export type Meal = S["MealOut"];
export type MealItem = S["MealItemOut"];
