"use client";

import { Pencil, Trash2 } from "lucide-react";
import { useState } from "react";

import { Field } from "@/components/form/field";
import { NumberInput } from "@/components/form/number-input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { Dialog, DialogClose, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import type { TrainingSession, TrainingSet, TrainingSetUpdate } from "@/lib/gateway/types";
import { queryKeys } from "@/lib/query/keys";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";

import { deleteSet, updateSet } from "../api";

const INVALIDATE = [["training", "list"] as const, ["training", "stats"] as const, ["dashboard"] as const];
const num = (s: string) => (s.trim() === "" ? null : Number(s));

function setLine(s: TrainingSet): string {
  if (s.distance_m != null || s.pace) {
    return [s.distance_m != null ? `${s.distance_m} m` : null, s.pace].filter(Boolean).join(" · ");
  }
  const load = [s.reps != null ? `${s.reps}` : null, s.weight_kg != null ? `× ${s.weight_kg} kg` : null]
    .filter(Boolean)
    .join(" ");
  const extra = [
    s.added_weight_kg != null ? `+${s.added_weight_kg} kg` : null,
    s.rpe != null ? `RPE ${s.rpe}` : null,
  ]
    .filter(Boolean)
    .join(" · ");
  return [load || "—", extra].filter(Boolean).join(" · ");
}

/** A single set with inline edit (dialog) and delete (confirm). */
export function SetRow({ sessionId, set, index }: { sessionId: number; set: TrainingSet; index: number }) {
  return (
    <li className="flex items-center gap-3 py-2 first:pt-0 last:pb-0">
      <span className="text-muted-foreground w-5 shrink-0 text-xs tabular-nums">{index + 1}</span>
      <span className="min-w-0 flex-1 truncate text-sm">
        <span className="font-medium">{set.exercise}</span>
        <span className="text-muted-foreground"> · {setLine(set)}</span>
      </span>
      {set.is_warmup ? <Badge variant="outline">warm-up</Badge> : null}
      <EditSetDialog sessionId={sessionId} set={set} />
      <DeleteSet sessionId={sessionId} set={set} />
    </li>
  );
}

function EditSetDialog({ sessionId, set }: { sessionId: number; set: TrainingSet }) {
  const [open, setOpen] = useState(false);
  const isSwim = set.distance_m != null || !!set.pace;
  const [exercise, setExercise] = useState(set.exercise);
  const [reps, setReps] = useState(set.reps != null ? String(set.reps) : "");
  const [weight, setWeight] = useState(set.weight_kg != null ? String(set.weight_kg) : "");
  const [added, setAdded] = useState(set.added_weight_kg != null ? String(set.added_weight_kg) : "");
  const [rpe, setRpe] = useState(set.rpe != null ? String(set.rpe) : "");
  const [distance, setDistance] = useState(set.distance_m != null ? String(set.distance_m) : "");
  const [pace, setPace] = useState(set.pace ?? "");
  const [warmup, setWarmup] = useState(set.is_warmup);

  const mutation = useGatewayMutation({
    mutationFn: (body: TrainingSetUpdate) => updateSet(sessionId, set.id, body),
    update: (qc, session: TrainingSession) =>
      qc.setQueryData(queryKeys.training.session(sessionId), session),
    invalidate: INVALIDATE,
    successMessage: "Set updated",
    onSuccess: () => setOpen(false),
  });

  function save() {
    mutation.mutate({
      exercise: exercise.trim() || undefined,
      reps: num(reps),
      weight_kg: num(weight),
      added_weight_kg: num(added),
      rpe: num(rpe),
      distance_m: num(distance),
      pace: pace.trim() || null,
      is_warmup: warmup,
    });
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Edit set" className="size-8">
          <Pencil className="size-4" />
        </Button>
      </DialogTrigger>
      <DialogContent title="Edit set" description="Fix a mistyped rep, weight, or exercise.">
        <div className="space-y-3">
          <Field id="set-exercise" label="Exercise">
            <Input id="set-exercise" value={exercise} onChange={(e) => setExercise(e.target.value)} />
          </Field>
          {isSwim ? (
            <div className="grid grid-cols-2 gap-3">
              <Field id="set-distance" label="Distance">
                <NumberInput
                  id="set-distance"
                  unit="m"
                  value={distance}
                  onChange={(e) => setDistance(e.target.value)}
                />
              </Field>
              <Field id="set-pace" label="Pace" hint="e.g. 1:45/100m">
                <Input id="set-pace" value={pace} onChange={(e) => setPace(e.target.value)} />
              </Field>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <Field id="set-reps" label="Reps">
                <NumberInput id="set-reps" value={reps} onChange={(e) => setReps(e.target.value)} />
              </Field>
              <Field id="set-weight" label="Weight">
                <NumberInput
                  id="set-weight"
                  unit="kg"
                  value={weight}
                  onChange={(e) => setWeight(e.target.value)}
                />
              </Field>
              <Field id="set-added" label="+Weight" hint="bodyweight">
                <NumberInput
                  id="set-added"
                  unit="kg"
                  value={added}
                  onChange={(e) => setAdded(e.target.value)}
                />
              </Field>
              <Field id="set-rpe" label="RPE" hint="0–10">
                <NumberInput id="set-rpe" step="0.5" value={rpe} onChange={(e) => setRpe(e.target.value)} />
              </Field>
            </div>
          )}

          <div className="flex items-center justify-between gap-2">
            <button
              type="button"
              aria-pressed={warmup}
              onClick={() => setWarmup((w) => !w)}
              className={cn(
                "rounded-md border px-2.5 py-1 text-xs font-medium transition-colors",
                warmup
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              Warm-up
            </button>
            <div className="flex gap-2">
              <DialogClose asChild>
                <Button type="button" variant="ghost">
                  Cancel
                </Button>
              </DialogClose>
              <Button type="button" onClick={save} loading={mutation.isPending}>
                Save
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function DeleteSet({ sessionId, set }: { sessionId: number; set: TrainingSet }) {
  const mutation = useGatewayMutation({
    mutationFn: () => deleteSet(sessionId, set.id),
    update: (qc, session: TrainingSession) =>
      qc.setQueryData(queryKeys.training.session(sessionId), session),
    invalidate: INVALIDATE,
    successMessage: "Set removed",
  });

  return (
    <ConfirmDialog
      trigger={
        <Button
          variant="ghost"
          size="icon"
          aria-label="Delete set"
          className="text-destructive size-8"
        >
          <Trash2 className="size-4" />
        </Button>
      }
      title="Remove this set?"
      description={`"${set.exercise}" will be removed from the session.`}
      confirmLabel="Remove"
      onConfirm={() => mutation.mutateAsync(undefined)}
    />
  );
}
