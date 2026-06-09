import { z } from "zod";

/** Empty string / null from a form field → undefined, then coerce to a number. */
const optionalNumber = z.preprocess(
  (v) => (v === "" || v == null ? undefined : v),
  z.coerce.number().nonnegative().optional(),
);
const optionalInt = z.preprocess(
  (v) => (v === "" || v == null ? undefined : v),
  z.coerce.number().int().nonnegative().optional(),
);
const optionalRpe = z.preprocess(
  (v) => (v === "" || v == null ? undefined : v),
  z.coerce.number().min(0).max(10).optional(),
);

export const newSessionSchema = z.object({
  type: z.enum(["gym", "swim"]),
  ts: z.string().min(1, "Pick a date & time"),
  duration_min: optionalInt,
  rpe: optionalRpe,
  notes: z.string().trim().optional(),
  // swim-only
  distance_m: optionalNumber,
  pace: z.string().trim().optional(),
});

export type NewSessionForm = z.input<typeof newSessionSchema>;
export type NewSessionValues = z.output<typeof newSessionSchema>;

export const addSetSchema = z.object({
  exercise: z.string().trim().min(1, "Pick an exercise"),
  reps: optionalInt,
  weight_kg: optionalNumber,
  added_weight_kg: optionalNumber,
  rpe: optionalRpe,
  is_warmup: z.boolean(),
});

export type AddSetForm = z.input<typeof addSetSchema>;
export type AddSetValues = z.output<typeof addSetSchema>;
