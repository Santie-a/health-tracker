"use client";

import { CheckCircle2, Pencil, Trash2, XCircle } from "lucide-react";
import { useState } from "react";

import { Field } from "@/components/form/field";
import { NumberInput } from "@/components/form/number-input";
import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { Dialog, DialogClose, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import type { Goal, GoalUpdate } from "@/lib/gateway/types";
import { queryKeys } from "@/lib/query/keys";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";

import { deleteGoal, updateGoal } from "../api";

const INVALIDATE = [queryKeys.goals.active, ["goals", "list"] as const, ["dashboard"] as const];
const num = (s: string) => (s.trim() === "" ? null : Number(s));

/** Edit a goal's targets, change its status, or delete it. */
export function EditGoalDialog({ goal }: { goal: Goal }) {
  const [open, setOpen] = useState(false);
  const isSleep = goal.category === "sleep";

  // Sleep target is stored in minutes but edited in hours.
  const [target, setTarget] = useState(
    goal.target_value == null ? "" : String(isSleep ? goal.target_value / 60 : goal.target_value),
  );
  const [rate, setRate] = useState(
    goal.target_rate_per_week == null ? "" : String(goal.target_rate_per_week),
  );
  const [targetDate, setTargetDate] = useState(goal.target_date ?? "");
  const [notes, setNotes] = useState(goal.notes ?? "");

  const update = useGatewayMutation({
    mutationFn: (body: GoalUpdate) => updateGoal(goal.id, body),
    invalidate: INVALIDATE,
    successMessage: "Goal updated",
    onSuccess: () => setOpen(false),
  });

  const remove = useGatewayMutation({
    mutationFn: () => deleteGoal(goal.id),
    invalidate: INVALIDATE,
    successMessage: "Goal deleted",
    onSuccess: () => setOpen(false),
  });

  function save() {
    const targetValue =
      target.trim() === "" ? null : isSleep ? Math.round(Number(target) * 60) : Number(target);
    update.mutate({
      target_value: targetValue,
      target_rate_per_week: isSleep ? null : num(rate),
      target_date: targetDate || null,
      notes: notes.trim() || null,
    });
  }

  const setStatus = (status: GoalUpdate["status"]) => update.mutate({ status });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Edit goal">
          <Pencil />
        </Button>
      </DialogTrigger>
      <DialogContent title="Edit goal" description="Adjust targets or change this goal's status.">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            save();
          }}
          className="space-y-4"
        >
          {isSleep ? (
            <Field id="edit-sleep-target" label="Nightly sleep target" hint="Hours per night">
              <NumberInput
                id="edit-sleep-target"
                step="0.25"
                unit="h"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
              />
            </Field>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              <Field id="edit-target" label="Target weight">
                <NumberInput
                  id="edit-target"
                  unit="kg"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                />
              </Field>
              <Field id="edit-rate" label="Weekly rate" hint="kg/wk (− to lose)">
                <NumberInput
                  id="edit-rate"
                  step="0.05"
                  value={rate}
                  onChange={(e) => setRate(e.target.value)}
                />
              </Field>
            </div>
          )}

          {!isSleep ? (
            <Field id="edit-target-date" label="Target date">
              <Input
                id="edit-target-date"
                type="date"
                value={targetDate}
                onChange={(e) => setTargetDate(e.target.value)}
              />
            </Field>
          ) : null}

          <Field id="edit-goal-notes" label="Notes">
            <Input id="edit-goal-notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
          </Field>

          {/* Status actions */}
          <div className="flex flex-wrap gap-2 border-t pt-3">
            {goal.status === "active" ? (
              <>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="text-success"
                  onClick={() => setStatus("achieved")}
                >
                  <CheckCircle2 /> Mark achieved
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setStatus("abandoned")}
                >
                  <XCircle /> Abandon
                </Button>
              </>
            ) : (
              <Button type="button" variant="outline" size="sm" onClick={() => setStatus("active")}>
                Reactivate
              </Button>
            )}
          </div>

          <div className="flex items-center justify-between gap-2">
            <ConfirmDialog
              trigger={
                <Button type="button" variant="ghost" size="sm" className="text-destructive">
                  <Trash2 /> Delete
                </Button>
              }
              title="Delete this goal?"
              description="This removes the goal and its history. This can't be undone."
              onConfirm={() => remove.mutateAsync(undefined)}
            />
            <div className="flex gap-2">
              <DialogClose asChild>
                <Button type="button" variant="ghost">
                  Cancel
                </Button>
              </DialogClose>
              <Button type="submit" loading={update.isPending}>
                Save
              </Button>
            </div>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
