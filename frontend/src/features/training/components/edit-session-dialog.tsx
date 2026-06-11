"use client";

import { Dumbbell, Pencil, Trash2, Waves } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Field } from "@/components/form/field";
import { NumberInput } from "@/components/form/number-input";
import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { Dialog, DialogClose, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Segmented } from "@/components/ui/segmented";
import type { TrainingSession, TrainingSessionUpdate } from "@/lib/gateway/types";
import { queryKeys } from "@/lib/query/keys";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";
import { formatInstant } from "@/lib/time";

import { deleteTrainingSession, updateTrainingSession } from "../api";

// Aggregate views to refresh — disjoint from the session's own key (updated/removed here).
const INVALIDATE = [["training", "list"] as const, ["training", "stats"] as const, ["dashboard"] as const];

const num = (s: string) => (s.trim() === "" ? null : Number(s));

/** Edit a session's fields, or delete it (with confirm). Lives in the session header. */
export function EditSessionDialog({ session }: { session: TrainingSession }) {
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const [type, setType] = useState<"gym" | "swim">(session.type === "swim" ? "swim" : "gym");
  const [ts, setTs] = useState(formatInstant(session.ts, "yyyy-MM-dd'T'HH:mm"));
  const [duration, setDuration] = useState(
    session.duration_min != null ? String(session.duration_min) : "",
  );
  const [rpe, setRpe] = useState(session.rpe != null ? String(session.rpe) : "");
  const [notes, setNotes] = useState(session.notes ?? "");

  const update = useGatewayMutation({
    mutationFn: (body: TrainingSessionUpdate) => updateTrainingSession(session.id, body),
    update: (qc, updated) => qc.setQueryData(queryKeys.training.session(session.id), updated),
    invalidate: INVALIDATE,
    successMessage: "Session updated",
    onSuccess: () => setOpen(false),
  });

  const remove = useGatewayMutation({
    mutationFn: () => deleteTrainingSession(session.id),
    invalidate: INVALIDATE,
    successMessage: "Session deleted",
    onSuccess: () => {
      router.push("/training");
    },
  });

  function save() {
    update.mutate({
      type,
      ts: new Date(ts).toISOString(),
      duration_min: num(duration),
      rpe: num(rpe),
      notes: notes.trim() || null,
    });
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm">
          <Pencil /> Edit
        </Button>
      </DialogTrigger>
      <DialogContent title="Edit session" description="Fix any detail of this session.">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            save();
          }}
          className="space-y-4"
        >
          <Segmented
            options={[
              { value: "gym", label: "Gym", icon: <Dumbbell className="size-4" /> },
              { value: "swim", label: "Swim", icon: <Waves className="size-4" /> },
            ]}
            value={type}
            onChange={setType}
          />

          <Field id="edit-ts" label="When">
            <Input
              id="edit-ts"
              type="datetime-local"
              value={ts}
              onChange={(e) => setTs(e.target.value)}
            />
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field id="edit-duration" label="Duration">
              <NumberInput
                id="edit-duration"
                unit="min"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
              />
            </Field>
            <Field id="edit-rpe" label="RPE" hint="0–10">
              <NumberInput
                id="edit-rpe"
                step="0.5"
                value={rpe}
                onChange={(e) => setRpe(e.target.value)}
              />
            </Field>
          </div>

          <Field id="edit-notes" label="Notes">
            <Input id="edit-notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
          </Field>

          <div className="flex items-center justify-between gap-2">
            <ConfirmDialog
              trigger={
                <Button type="button" variant="ghost" size="sm" className="text-destructive">
                  <Trash2 /> Delete session
                </Button>
              }
              title="Delete this session?"
              description="This removes the session and all of its sets. This can't be undone."
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
