import { z } from "zod";

/** Empty string / null → undefined, then coerce (nonnegative). */
const optionalNumber = z.preprocess(
  (v) => (v === "" || v == null ? undefined : v),
  z.coerce.number().nonnegative().optional(),
);
/** Like optionalNumber but signed — a rate can be negative (fat loss). */
const optionalSignedNumber = z.preprocess(
  (v) => (v === "" || v == null ? undefined : v),
  z.coerce.number().optional(),
);

export const newGoalSchema = z.object({
  type: z.enum(["gain_muscle", "gain_weight", "lose_fat", "recomp", "maintain", "improve_sleep"]),
  target_value: optionalNumber,
  target_rate_per_week: optionalSignedNumber,
  target_date: z.string().trim().optional(),
  notes: z.string().trim().optional(),
});

export type NewGoalForm = z.input<typeof newGoalSchema>;
export type NewGoalValues = z.output<typeof newGoalSchema>;
