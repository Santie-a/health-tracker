import type { components } from "./types.gen";

/**
 * Friendly aliases over the generated OpenAPI schemas. Features import domain types
 * from here (not the generated file) so the indirection is in one place and the
 * generated output stays an implementation detail. Pure types — safe on the client.
 */
type S = components["schemas"];

export type Dashboard = S["DashboardOut"];
export type TelemetrySummary = S["TelemetrySummary"];
export type SleepNight = S["SleepNight"];
export type BodyCompositionPoint = S["BodyCompositionPoint"];
export type DailyRollup = S["DailyRollup"];
export type IngestResponse = S["IngestResponse"];
export type Totals = S["Totals"];
export type RecommendationItem = S["RecommendationItem"];
export type RecommendationsOut = S["RecommendationsOut"];
export type FeedbackIn = S["FeedbackIn"];

export type TrainingSession = S["TrainingSessionOut"];
export type TrainingSet = S["TrainingSetOut"];
export type TrainingSessionIn = S["TrainingSessionIn"];
export type TrainingSetIn = S["TrainingSetIn"];
export type TrainingSessionUpdate = S["TrainingSessionUpdate"];
export type TrainingSetUpdate = S["TrainingSetUpdate"];

export type Exercise = S["ExerciseOut"];
export type ExerciseIn = S["ExerciseIn"];
export type ExerciseUpdate = S["ExerciseUpdate"];

export type TrainingStats = S["TrainingStats"];

export type Meal = S["MealOut"];
export type MealItem = S["MealItemOut"];
export type MealIn = S["MealIn"];
export type MealItemAddIn = S["MealItemAddIn"];
export type AddItemsIn = S["AddItemsIn"];
export type MealUpdate = S["MealUpdate"];
export type MealItemUpdate = S["MealItemUpdate"];
export type DayNutrition = S["DayNutrition"];
export type MealCreateResponse = S["MealCreateResponse"];

export type Food = S["FoodOut"];
export type FoodResolve = S["FoodResolveOut"];
