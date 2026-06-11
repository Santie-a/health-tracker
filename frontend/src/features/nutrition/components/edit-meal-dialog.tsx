"use client";

import { Pencil, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Field } from "@/components/form/field";
import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { Dialog, DialogClose, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import type { Meal } from "@/lib/gateway/types";
import { queryKeys } from "@/lib/query/keys";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";
import { formatInstant } from "@/lib/time";

import { deleteMeal, updateMeal } from "../api";

// Aggregate views to refresh after an edit/delete — kept DISJOINT from the meal's own
// key, which is updated authoritatively (or removed) here.
const INVALIDATE = [["nutrition", "day"] as const, ["dashboard"] as const];

/** Edit a meal's name/time, or delete it (with confirm). Lives in the meal header. */
export function EditMealDialog({ meal }: { meal: Meal }) {
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const [name, setName] = useState(meal.name ?? "");
  const [ts, setTs] = useState(formatInstant(meal.ts, "yyyy-MM-dd'T'HH:mm"));

  const update = useGatewayMutation({
    mutationFn: () =>
      updateMeal(meal.id, { name: name.trim() || null, ts: new Date(ts).toISOString() }),
    update: (qc, updated) => qc.setQueryData(queryKeys.nutrition.meal(meal.id), updated),
    invalidate: INVALIDATE,
    successMessage: "Meal updated",
    onSuccess: () => setOpen(false),
  });

  const remove = useGatewayMutation({
    mutationFn: () => deleteMeal(meal.id),
    invalidate: INVALIDATE,
    successMessage: "Meal deleted",
    onSuccess: () => {
      router.push("/nutrition");
    },
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm">
          <Pencil /> Edit
        </Button>
      </DialogTrigger>
      <DialogContent title="Edit meal" description="Fix the name or time of this meal.">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            update.mutate(undefined);
          }}
          className="space-y-4"
        >
          <Field id="meal-name" label="Name">
            <Input
              id="meal-name"
              value={name}
              placeholder="optional"
              onChange={(e) => setName(e.target.value)}
            />
          </Field>
          <Field id="meal-ts" label="When">
            <Input
              id="meal-ts"
              type="datetime-local"
              value={ts}
              onChange={(e) => setTs(e.target.value)}
            />
          </Field>

          <div className="flex items-center justify-between gap-2">
            <ConfirmDialog
              trigger={
                <Button type="button" variant="ghost" size="sm" className="text-destructive">
                  <Trash2 /> Delete meal
                </Button>
              }
              title="Delete this meal?"
              description="This removes the meal and all of its items. This can't be undone."
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
