"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Plus } from "lucide-react";
import { useState } from "react";
import { useForm, useWatch } from "react-hook-form";

import { Field } from "@/components/form/field";
import { NumberInput } from "@/components/form/number-input";
import { Button } from "@/components/ui/button";
import { Dialog, DialogClose, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import type { GoalIn, GoalType } from "@/lib/gateway/types";
import { queryKeys } from "@/lib/query/keys";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";
import { cn } from "@/lib/utils";

import { GOAL_TYPE_HINT, GOAL_TYPE_LABEL } from "../meta";
import { createGoal } from "../api";
import { newGoalSchema, type NewGoalForm, type NewGoalValues } from "../schemas";

const TYPES: GoalType[] = [
  "gain_muscle",
  "gain_weight",
  "lose_fat",
  "recomp",
  "maintain",
  "improve_sleep",
];
const INVALIDATE = [queryKeys.goals.active, ["goals", "list"] as const, ["dashboard"] as const];

export function NewGoalDialog() {
  const [open, setOpen] = useState(false);
  const form = useForm<NewGoalForm, unknown, NewGoalValues>({
    resolver: zodResolver(newGoalSchema),
    defaultValues: { type: "gain_muscle" },
  });
  const { register, handleSubmit, control, setValue, reset, formState } = form;
  const type = useWatch({ control, name: "type" });
  const isSleep = type === "improve_sleep";

  const mutation = useGatewayMutation({
    mutationFn: createGoal,
    form,
    successMessage: "Goal created",
    invalidate: INVALIDATE,
    onSuccess: () => {
      reset({ type: "gain_muscle" });
      setOpen(false);
    },
  });

  const onSubmit = handleSubmit((values) => {
    // Sleep target is entered in hours; the gateway stores sleep_min in minutes.
    const targetValue =
      values.target_value == null
        ? null
        : isSleep
          ? Math.round(values.target_value * 60)
          : values.target_value;

    const body: GoalIn = {
      type: values.type,
      target_value: targetValue,
      target_rate_per_week: isSleep ? null : (values.target_rate_per_week ?? null),
      target_date: values.target_date || null,
      notes: values.notes || null,
    };
    mutation.mutate(body);
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Plus /> New goal
        </Button>
      </DialogTrigger>
      <DialogContent
        title="Set a goal"
        description="Pick a goal; we fill in sensible targets you can tweak."
      >
        <form onSubmit={onSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-2">
            {TYPES.map((t) => (
              <button
                key={t}
                type="button"
                aria-pressed={type === t}
                onClick={() => setValue("type", t)}
                className={cn(
                  "rounded-lg border p-2.5 text-left transition-colors",
                  type === t
                    ? "border-primary bg-accent"
                    : "hover:border-foreground/30 text-muted-foreground",
                )}
              >
                <span className="text-foreground block text-sm font-medium">
                  {GOAL_TYPE_LABEL[t]}
                </span>
              </button>
            ))}
          </div>
          <p className="text-muted-foreground text-xs">{GOAL_TYPE_HINT[type]}</p>

          {isSleep ? (
            <Field
              id="sleep-target"
              label="Nightly sleep target"
              hint="Hours per night (default 7.5)"
              error={formState.errors.target_value?.message}
            >
              <NumberInput
                id="sleep-target"
                step="0.25"
                unit="h"
                placeholder="7.5"
                {...register("target_value")}
              />
            </Field>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              <Field
                id="target-value"
                label="Target weight"
                hint="optional"
                error={formState.errors.target_value?.message}
              >
                <NumberInput
                  id="target-value"
                  unit="kg"
                  placeholder="—"
                  {...register("target_value")}
                />
              </Field>
              <Field
                id="target-rate"
                label="Weekly rate"
                hint="kg/wk (− to lose)"
                error={formState.errors.target_rate_per_week?.message}
              >
                <NumberInput
                  id="target-rate"
                  step="0.05"
                  placeholder="auto"
                  {...register("target_rate_per_week")}
                />
              </Field>
            </div>
          )}

          {!isSleep ? (
            <Field id="target-date" label="Target date" hint="optional">
              <Input id="target-date" type="date" {...register("target_date")} />
            </Field>
          ) : null}

          <Field id="goal-notes" label="Notes" error={formState.errors.notes?.message}>
            <Input id="goal-notes" placeholder="optional" {...register("notes")} />
          </Field>

          <div className="flex justify-end gap-2">
            <DialogClose asChild>
              <Button type="button" variant="ghost">
                Cancel
              </Button>
            </DialogClose>
            <Button type="submit" loading={mutation.isPending}>
              Create goal
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
