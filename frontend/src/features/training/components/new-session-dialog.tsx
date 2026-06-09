"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { format } from "date-fns";
import { Dumbbell, Plus, Waves } from "lucide-react";
import { useState } from "react";
import { useForm, useWatch } from "react-hook-form";

import { Field } from "@/components/form/field";
import { NumberInput } from "@/components/form/number-input";
import { Button } from "@/components/ui/button";
import { Dialog, DialogClose, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Segmented } from "@/components/ui/segmented";
import type { TrainingSessionIn, TrainingSetIn } from "@/lib/gateway/types";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";

import { createTrainingSession } from "../api";
import { newSessionSchema, type NewSessionForm, type NewSessionValues } from "../schemas";

function nowLocalInput(): string {
  return format(new Date(), "yyyy-MM-dd'T'HH:mm");
}

/** Quick-capture form for a gym or swim session. Swim distance/pace ride on an inline set. */
export function NewSessionDialog() {
  const [open, setOpen] = useState(false);
  const form = useForm<NewSessionForm, unknown, NewSessionValues>({
    resolver: zodResolver(newSessionSchema),
    defaultValues: { type: "gym", ts: nowLocalInput() },
  });
  const { register, handleSubmit, control, setValue, reset, formState } = form;
  const type = useWatch({ control, name: "type" });

  const mutation = useGatewayMutation({
    mutationFn: createTrainingSession,
    form,
    successMessage: "Session logged",
    invalidate: [["dashboard"], ["training"]],
    onSuccess: () => {
      reset({ type, ts: nowLocalInput() } as NewSessionForm);
      setOpen(false);
    },
  });

  const onSubmit = handleSubmit((values) => {
    const sets: TrainingSetIn[] = [];
    if (values.type === "swim" && (values.distance_m != null || values.pace)) {
      sets.push({
        exercise: "freestyle",
        distance_m: values.distance_m ?? null,
        pace: values.pace || null,
        is_warmup: false,
      });
    }
    const body: TrainingSessionIn = {
      ts: new Date(values.ts).toISOString(),
      type: values.type,
      duration_min: values.duration_min ?? null,
      rpe: values.rpe ?? null,
      notes: values.notes || null,
      sets,
    };
    mutation.mutate(body);
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Plus /> New session
        </Button>
      </DialogTrigger>
      <DialogContent title="Log a session" description="Manual training entry.">
        <form onSubmit={onSubmit} className="space-y-4">
          <Segmented
            options={[
              { value: "gym", label: "Gym", icon: <Dumbbell className="size-4" /> },
              { value: "swim", label: "Swim", icon: <Waves className="size-4" /> },
            ]}
            value={type}
            onChange={(v) => setValue("type", v)}
          />

          <Field id="ts" label="When" error={formState.errors.ts?.message}>
            <Input id="ts" type="datetime-local" {...register("ts")} />
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field
              id="duration_min"
              label="Duration"
              error={formState.errors.duration_min?.message}
            >
              <NumberInput
                id="duration_min"
                unit="min"
                placeholder="0"
                {...register("duration_min")}
              />
            </Field>
            <Field id="rpe" label="RPE" hint="0–10" error={formState.errors.rpe?.message}>
              <NumberInput id="rpe" step="0.5" placeholder="0" {...register("rpe")} />
            </Field>
          </div>

          {type === "swim" ? (
            <div className="grid grid-cols-2 gap-3">
              <Field id="distance_m" label="Distance" error={formState.errors.distance_m?.message}>
                <NumberInput id="distance_m" unit="m" placeholder="0" {...register("distance_m")} />
              </Field>
              <Field id="pace" label="Pace" hint="e.g. 1:45/100m">
                <Input id="pace" placeholder="1:45/100m" {...register("pace")} />
              </Field>
            </div>
          ) : null}

          <Field id="notes" label="Notes" error={formState.errors.notes?.message}>
            <Input id="notes" placeholder="optional" {...register("notes")} />
          </Field>

          <div className="flex justify-end gap-2">
            <DialogClose asChild>
              <Button type="button" variant="ghost">
                Cancel
              </Button>
            </DialogClose>
            <Button type="submit" loading={mutation.isPending}>
              Log session
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
