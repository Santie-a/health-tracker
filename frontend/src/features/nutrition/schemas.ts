import { z } from "zod";

const optionalNumber = z.preprocess(
  (v) => (v === "" || v == null ? undefined : v),
  z.coerce.number().nonnegative().optional(),
);

/** New (empty) meal — name + time; items are added on the meal detail page. */
export const newMealSchema = z.object({
  name: z.string().trim().optional(),
  ts: z.string().min(1, "Pick a date & time"),
});
export type NewMealForm = z.input<typeof newMealSchema>;
export type NewMealValues = z.output<typeof newMealSchema>;

/** Raw kcal quick-add: a name + kcal, optional macros. */
export const rawItemSchema = z.object({
  food: z.string().trim().min(1, "Name the item"),
  kcal: z.preprocess(
    (v) => (v === "" || v == null ? undefined : v),
    z.coerce.number().nonnegative({ message: "kcal required" }),
  ),
  protein_g: optionalNumber,
  carbs_g: optionalNumber,
  fat_g: optionalNumber,
});
export type RawItemForm = z.input<typeof rawItemSchema>;
export type RawItemValues = z.output<typeof rawItemSchema>;
