"use client";

import { useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Pencil, Trash2 } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import { EmptyState } from "@/components/async/empty-state";
import { QueryState } from "@/components/async/query-state";
import { Skeleton } from "@/components/async/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { Dialog, DialogClose, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { Field } from "@/components/form/field";
import { Input } from "@/components/ui/input";
import type { Exercise, ExerciseUpdate } from "@/lib/gateway/types";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";
import { useDebouncedValue } from "@/lib/use-debounced-value";

import { deleteExercise, updateExercise } from "../api";
import { useExerciseSearch } from "../hooks";

const CATEGORIES = ["push", "pull", "squat", "hinge", "carry", "core", "swim", "other"] as const;
const INVALIDATE = [["exercises"] as const, ["training", "stats"] as const];

/** Manage the exercise catalog: search, edit details, delete (or deactivate). */
export function ExerciseCatalogView() {
  const [q, setQ] = useState("");
  const debounced = useDebouncedValue(q.trim(), 250);
  const query = useExerciseSearch({ q: debounced, limit: 200 }, true);

  return (
    <div className="space-y-4">
      <Link
        href="/training"
        className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 text-sm"
      >
        <ArrowLeft className="size-4" /> Training
      </Link>

      <h1 className="text-2xl font-semibold tracking-tight">Exercise catalog</h1>

      <Input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search exercises…"
        autoComplete="off"
      />

      <QueryState
        query={query}
        loading={<Skeleton className="h-64 w-full" />}
        isEmpty={(rows) => rows.length === 0}
        empty={<EmptyState title="No exercises" description="Nothing matches your search." />}
      >
        {(rows) => (
          <ul className="divide-y rounded-xl border">
            {rows.map((ex) => (
              <ExerciseRow key={ex.id} exercise={ex} />
            ))}
          </ul>
        )}
      </QueryState>
    </div>
  );
}

function ExerciseRow({ exercise }: { exercise: Exercise }) {
  return (
    <li className="flex items-center gap-3 px-3 py-2.5">
      <div className="min-w-0 flex-1">
        <p className="flex items-center gap-2 truncate text-sm">
          <span className="font-medium">{exercise.name}</span>
          {exercise.category ? <Badge variant="outline">{exercise.category}</Badge> : null}
          {!exercise.is_active ? <Badge variant="info">inactive</Badge> : null}
        </p>
        {exercise.primary_muscle ? (
          <p className="text-muted-foreground text-xs">{exercise.primary_muscle}</p>
        ) : null}
      </div>
      <EditExerciseDialog exercise={exercise} />
      <DeleteExercise exercise={exercise} />
    </li>
  );
}

function EditExerciseDialog({ exercise }: { exercise: Exercise }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState(exercise.name);
  const [category, setCategory] = useState(exercise.category ?? "");
  const [primary, setPrimary] = useState(exercise.primary_muscle ?? "");
  const [equipment, setEquipment] = useState(exercise.equipment ?? "");
  const [aliases, setAliases] = useState((exercise.aliases ?? []).join(", "));

  const mutation = useGatewayMutation({
    mutationFn: (body: ExerciseUpdate) => updateExercise(exercise.id, body),
    invalidate: INVALIDATE,
    successMessage: "Exercise updated",
    onSuccess: () => setOpen(false),
  });

  function save() {
    const aliasList = aliases
      .split(",")
      .map((a) => a.trim())
      .filter(Boolean);
    mutation.mutate({
      name: name.trim() || undefined,
      category: (category || null) as ExerciseUpdate["category"],
      primary_muscle: primary.trim() || null,
      equipment: equipment.trim() || null,
      aliases: aliasList.length ? aliasList : null,
    });
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Edit exercise" className="size-8">
          <Pencil className="size-4" />
        </Button>
      </DialogTrigger>
      <DialogContent title="Edit exercise" description="Renaming updates how stats group this lift.">
        <div className="space-y-3">
          <Field id="ex-name" label="Name">
            <Input id="ex-name" value={name} onChange={(e) => setName(e.target.value)} />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field id="ex-category" label="Category">
              <select
                id="ex-category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="bg-background focus-visible:ring-ring h-9 w-full rounded-md border px-3 text-sm focus-visible:ring-2 focus-visible:outline-none"
              >
                <option value="">—</option>
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </Field>
            <Field id="ex-primary" label="Primary muscle">
              <Input id="ex-primary" value={primary} onChange={(e) => setPrimary(e.target.value)} />
            </Field>
          </div>
          <Field id="ex-equipment" label="Equipment">
            <Input
              id="ex-equipment"
              value={equipment}
              onChange={(e) => setEquipment(e.target.value)}
            />
          </Field>
          <Field id="ex-aliases" label="Aliases" hint="comma-separated">
            <Input id="ex-aliases" value={aliases} onChange={(e) => setAliases(e.target.value)} />
          </Field>
          <div className="flex justify-end gap-2">
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
      </DialogContent>
    </Dialog>
  );
}

function DeleteExercise({ exercise }: { exercise: Exercise }) {
  const qc = useQueryClient();
  const mutation = useGatewayMutation({
    mutationFn: () => deleteExercise(exercise.id),
    invalidate: INVALIDATE,
    onSuccess: (res) => {
      void qc.invalidateQueries({ queryKey: ["exercises"] });
      toast.success(
        res.action === "deactivated"
          ? "Exercise deactivated (kept for logged history)"
          : "Exercise deleted",
      );
    },
  });

  return (
    <ConfirmDialog
      trigger={
        <Button
          variant="ghost"
          size="icon"
          aria-label="Delete exercise"
          className="text-destructive size-8"
        >
          <Trash2 className="size-4" />
        </Button>
      }
      title="Delete this exercise?"
      description="If any logged set uses it, it's deactivated instead of deleted so your history stays intact."
      onConfirm={() => mutation.mutateAsync(undefined)}
    />
  );
}
