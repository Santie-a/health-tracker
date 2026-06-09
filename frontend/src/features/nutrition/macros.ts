import type { Food } from "@/lib/gateway/types";

export interface Macros {
  kcal: number | null;
  protein_g: number | null;
  carbs_g: number | null;
  fat_g: number | null;
}

/** Per-100g macros scaled to `grams` — the client-side live preview (gateway is source of truth on save). */
export function macrosForGrams(food: Food, grams: number): Macros {
  const f = grams / 100;
  const s = (per100: number | null | undefined) => (per100 != null ? Math.round(per100 * f) : null);
  return {
    kcal: s(food.kcal_100g),
    protein_g: s(food.protein_100g),
    carbs_g: s(food.carbs_100g),
    fat_g: s(food.fat_100g),
  };
}

/** "≈ 320 kcal · 12P / 40C / 8F" — compact macro summary. */
export function formatMacros(m: Macros): string {
  const macros = [
    m.protein_g != null ? `${m.protein_g}P` : null,
    m.carbs_g != null ? `${m.carbs_g}C` : null,
    m.fat_g != null ? `${m.fat_g}F` : null,
  ].filter(Boolean);
  const kcal = m.kcal != null ? `${m.kcal} kcal` : "—";
  return macros.length ? `${kcal} · ${macros.join(" / ")}` : kcal;
}
