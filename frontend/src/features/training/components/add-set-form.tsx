"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Plus, RotateCcw } from "lucide-react";
import { useForm, useWatch } from "react-hook-form";

import { Field } from "@/components/form/field";
import { NumberInput } from "@/components/form/number-input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { TrainingSet, TrainingSetIn } from "@/lib/gateway/types";
import { queryKeys } from "@/lib/query/keys";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";

import { addSets } from "../api";
import { addSetSchema, type AddSetForm as AddSetFormInput, type AddSetValues } from "../schemas";
import { ExerciseCombobox } from "./exercise-combobox";

/**
 * Fast set entry under a session. Keeps the exercise + weight after a successful add so
 * "+ Add set" is one tap for the next set; "Repeat last" copies the session's last set.
 */
export function AddSetForm({ sessionId, lastSet }: { sessionId: number; lastSet?: TrainingSet }) {
  const form = useForm<AddSetFormInput, unknown, AddSetValues>({
    resolver: zodResolver(addSetSchema),
    defaultValues: {
      exercise: lastSet?.exercise ?? "",
      reps: "",
      weight_kg: "",
      added_weight_kg: "",
      rpe: "",
      is_warmup: false,
    },
  });
  const { register, handleSubmit, control, setValue, reset, formState } = form;
  const exercise = useWatch({ control, name: "exercise" });
  const isWarmup = useWatch({ control, name: "is_warmup" });

  const mutation = useGatewayMutation({
    mutationFn: (set: TrainingSetIn) => addSets(sessionId, [set]),
    form,
    // The response is the full updated session → write it straight to the cache
    // (race-free). Aggregates (list, dashboard) are disjoint keys, refreshed separately.
    update: (qc, session) => qc.setQueryData(queryKeys.training.session(sessionId), session),
    invalidate: [["training", "list"], ["dashboard"]],
    onSuccess: (_data, set) => {
      // Keep exercise + weight for the next set; clear reps + warmup.
      reset({
        exercise: set.exercise,
        weight_kg: set.weight_kg != null ? String(set.weight_kg) : "",
        added_weight_kg: set.added_weight_kg != null ? String(set.added_weight_kg) : "",
        reps: "",
        rpe: "",
        is_warmup: false,
      });
    },
  });

  const onSubmit = handleSubmit((values) => {
    mutation.mutate({
      exercise: values.exercise,
      reps: values.reps ?? null,
      weight_kg: values.weight_kg ?? null,
      added_weight_kg: values.added_weight_kg ?? null,
      rpe: values.rpe ?? null,
      is_warmup: values.is_warmup,
    });
  });

  function repeatLast() {
    if (!lastSet) return;
    reset({
      exercise: lastSet.exercise,
      reps: lastSet.reps != null ? String(lastSet.reps) : "",
      weight_kg: lastSet.weight_kg != null ? String(lastSet.weight_kg) : "",
      added_weight_kg: lastSet.added_weight_kg != null ? String(lastSet.added_weight_kg) : "",
      rpe: lastSet.rpe != null ? String(lastSet.rpe) : "",
      is_warmup: lastSet.is_warmup,
    });
  }

  return (
    <form onSubmit={onSubmit} className="space-y-3 rounded-xl border p-3">
      <Field id="exercise" label="Exercise" error={formState.errors.exercise?.message}>
        <ExerciseCombobox
          value={exercise}
          onChange={(name) => setValue("exercise", name, { shouldValidate: formState.isSubmitted })}
          invalid={!!formState.errors.exercise}
        />
      </Field>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Field id="reps" label="Reps" error={formState.errors.reps?.message}>
          <NumberInput id="reps" placeholder="0" {...register("reps")} />
        </Field>
        <Field id="weight_kg" label="Weight" error={formState.errors.weight_kg?.message}>
          <NumberInput id="weight_kg" unit="kg" placeholder="0" {...register("weight_kg")} />
        </Field>
        <Field
          id="added_weight_kg"
          label="+Weight"
          hint="bodyweight"
          error={formState.errors.added_weight_kg?.message}
        >
          <NumberInput
            id="added_weight_kg"
            unit="kg"
            placeholder="0"
            {...register("added_weight_kg")}
          />
        </Field>
        <Field id="rpe" label="RPE" hint="0–10" error={formState.errors.rpe?.message}>
          <NumberInput id="rpe" step="0.5" placeholder="0" {...register("rpe")} />
        </Field>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          aria-pressed={isWarmup}
          onClick={() => setValue("is_warmup", !isWarmup)}
          className={cn(
            "rounded-md border px-2.5 py-1 text-xs font-medium transition-colors",
            isWarmup
              ? "bg-accent text-accent-foreground"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          Warm-up
        </button>
        {lastSet ? (
          <Button type="button" variant="ghost" size="sm" onClick={repeatLast}>
            <RotateCcw /> Repeat last
          </Button>
        ) : null}
        <Button type="submit" size="sm" className="ml-auto" loading={mutation.isPending}>
          <Plus /> Add set
        </Button>
      </div>
    </form>
  );
}
