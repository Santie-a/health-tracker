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
import type { Meal, MealItem, MealItemUpdate } from "@/lib/gateway/types";
import { queryKeys } from "@/lib/query/keys";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";

import { deleteMealItem, updateMealItem } from "../api";

const round = (n: number) => Math.round(n).toLocaleString();
const INVALIDATE = [["nutrition", "day"] as const, ["dashboard"] as const];

function amount(it: MealItem): string {
  if (it.portion_label) return `${it.portion_label}${it.qty && it.qty !== 1 ? ` × ${it.qty}` : ""}`;
  if (it.grams != null) return `${it.grams} g`;
  return "";
}

/** A single meal item with inline edit (dialog) and delete (confirm). */
export function MealItemRow({ mealId, item }: { mealId: number; item: MealItem }) {
  return (
    <li className="flex items-center gap-3 py-2 first:pt-0 last:pb-0">
      <div className="min-w-0 flex-1">
        <p className="flex items-center gap-2 truncate text-sm">
          <span className="font-medium">{item.food}</span>
          {amount(item) ? <span className="text-muted-foreground">{amount(item)}</span> : null}
          {item.estimated ? <Badge variant="info">estimated</Badge> : null}
        </p>
      </div>
      <span className="text-muted-foreground shrink-0 text-sm tabular-nums">
        {item.kcal != null ? `${round(item.kcal)} kcal` : "—"}
      </span>
      <EditItemDialog mealId={mealId} item={item} />
      <DeleteItem mealId={mealId} item={item} />
    </li>
  );
}

function EditItemDialog({ mealId, item }: { mealId: number; item: MealItem }) {
  const [open, setOpen] = useState(false);
  const [food, setFood] = useState(item.food);
  const [grams, setGrams] = useState(item.grams != null ? String(item.grams) : "");
  const [kcal, setKcal] = useState(item.kcal != null ? String(item.kcal) : "");
  const [protein, setProtein] = useState(item.protein_g != null ? String(item.protein_g) : "");
  const [carbs, setCarbs] = useState(item.carbs_g != null ? String(item.carbs_g) : "");
  const [fat, setFat] = useState(item.fat_g != null ? String(item.fat_g) : "");

  const mutation = useGatewayMutation({
    mutationFn: (body: MealItemUpdate) => updateMealItem(mealId, item.id, body),
    update: (qc, meal: Meal) => qc.setQueryData(queryKeys.nutrition.meal(mealId), meal),
    invalidate: INVALIDATE,
    successMessage: "Item updated",
    onSuccess: () => setOpen(false),
  });

  const num = (s: string) => (s.trim() === "" ? undefined : Number(s));

  function save() {
    // Omit blank macros so the gateway re-estimates from grams when they're cleared.
    mutation.mutate({
      food: food.trim() || undefined,
      grams: num(grams),
      kcal: num(kcal),
      protein_g: num(protein),
      carbs_g: num(carbs),
      fat_g: num(fat),
    });
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Edit item" className="size-8">
          <Pencil className="size-4" />
        </Button>
      </DialogTrigger>
      <DialogContent
        title="Edit item"
        description="Clear the macros to re-estimate them from grams."
      >
        <div className="space-y-3">
          <Field id="item-food" label="Food">
            <Input id="item-food" value={food} onChange={(e) => setFood(e.target.value)} />
          </Field>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
            <Field id="item-grams" label="Grams">
              <NumberInput
                id="item-grams"
                unit="g"
                value={grams}
                onChange={(e) => setGrams(e.target.value)}
              />
            </Field>
            <Field id="item-kcal" label="kcal">
              <NumberInput id="item-kcal" value={kcal} onChange={(e) => setKcal(e.target.value)} />
            </Field>
            <Field id="item-p" label="Protein">
              <NumberInput
                id="item-p"
                unit="g"
                value={protein}
                onChange={(e) => setProtein(e.target.value)}
              />
            </Field>
            <Field id="item-c" label="Carbs">
              <NumberInput
                id="item-c"
                unit="g"
                value={carbs}
                onChange={(e) => setCarbs(e.target.value)}
              />
            </Field>
            <Field id="item-f" label="Fat">
              <NumberInput id="item-f" unit="g" value={fat} onChange={(e) => setFat(e.target.value)} />
            </Field>
          </div>
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

function DeleteItem({ mealId, item }: { mealId: number; item: MealItem }) {
  const mutation = useGatewayMutation({
    mutationFn: () => deleteMealItem(mealId, item.id),
    update: (qc, meal: Meal) => qc.setQueryData(queryKeys.nutrition.meal(mealId), meal),
    invalidate: INVALIDATE,
    successMessage: "Item removed",
  });

  return (
    <ConfirmDialog
      trigger={
        <Button
          variant="ghost"
          size="icon"
          aria-label="Delete item"
          className="text-destructive size-8"
        >
          <Trash2 className="size-4" />
        </Button>
      }
      title="Remove this item?"
      description={`"${item.food}" will be removed from the meal.`}
      confirmLabel="Remove"
      onConfirm={() => mutation.mutateAsync(undefined)}
    />
  );
}
