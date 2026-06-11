import type {
  AddItemsIn,
  DayNutrition,
  Food,
  FoodResolve,
  Meal,
  MealCreateResponse,
  MealIn,
  MealItemUpdate,
  MealUpdate,
} from "@/lib/gateway/types";
import { apiGet, apiSend } from "@/lib/query/fetcher";

export function getDayNutrition(date: string): Promise<DayNutrition> {
  return apiGet<DayNutrition>("/api/meals", { date });
}

export function getMeal(id: number): Promise<Meal> {
  return apiGet<Meal>(`/api/meals/${id}`);
}

export function createMeal(body: MealIn): Promise<Meal> {
  return apiSend<Meal>("/api/meals", { json: body });
}

/** Multipart upload → image-svc (or degraded manual meal when it's offline). */
export function createPhotoMeal(form: FormData): Promise<MealCreateResponse> {
  return apiSend<MealCreateResponse>("/api/meals/photo", { body: form });
}

export function addMealItems(id: number, items: AddItemsIn["items"]): Promise<Meal> {
  return apiSend<Meal>(`/api/meals/${id}/items`, { json: { items } });
}

export function updateMeal(id: number, body: MealUpdate): Promise<Meal> {
  return apiSend<Meal>(`/api/meals/${id}`, { method: "PATCH", json: body });
}

export function deleteMeal(id: number): Promise<void> {
  return apiSend<void>(`/api/meals/${id}`, { method: "DELETE" });
}

/** Edit one item; the gateway returns the updated meal. */
export function updateMealItem(id: number, itemId: number, body: MealItemUpdate): Promise<Meal> {
  return apiSend<Meal>(`/api/meals/${id}/items/${itemId}`, { method: "PATCH", json: body });
}

/** Remove one item; the gateway returns the updated meal. */
export function deleteMealItem(id: number, itemId: number): Promise<Meal> {
  return apiSend<Meal>(`/api/meals/${id}/items/${itemId}`, { method: "DELETE" });
}

export function searchFoods(q: string, limit = 8): Promise<Food[]> {
  return apiGet<Food[]>("/api/foods", { q, limit });
}

export function recentFoods(): Promise<Food[]> {
  return apiGet<Food[]>("/api/foods/recent");
}

export function resolveFood(name: string): Promise<FoodResolve> {
  return apiGet<FoodResolve>("/api/foods/resolve", { name });
}
