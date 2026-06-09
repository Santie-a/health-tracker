"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Plus } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Field } from "@/components/form/field";
import { NumberInput } from "@/components/form/number-input";
import { QueryState } from "@/components/async/query-state";
import { Button } from "@/components/ui/button";
import { Segmented } from "@/components/ui/segmented";
import type { Food, MealItemAddIn } from "@/lib/gateway/types";
import { queryKeys } from "@/lib/query/keys";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";

import { addMealItems } from "../api";
import { useRecentFoods } from "../hooks";
import { formatMacros, macrosForGrams } from "../macros";
import { rawItemSchema, type RawItemForm, type RawItemValues } from "../schemas";
import { FoodCombobox } from "./food-combobox";

const GRAMS = "__grams__";
// Aggregate views to refresh on a successful add. Kept DISJOINT from the meal's own key
// (["nutrition","meal",id]) — that one is updated authoritatively via `update`, so a
// racy refetch must not match and clobber it. "day" only matches ["nutrition","day",…].
const INVALIDATE = [["nutrition", "day"] as const, ["dashboard"] as const];

/** Search + serving picker with a live macro preview, plus a raw-kcal quick mode. */
export function AddItemForm({ mealId }: { mealId: number }) {
  const [mode, setMode] = useState<"search" | "kcal">("search");
  return (
    <div className="space-y-3 rounded-xl border p-3">
      <Segmented
        size="sm"
        options={[
          { value: "search", label: "Search" },
          { value: "kcal", label: "Quick kcal" },
        ]}
        value={mode}
        onChange={setMode}
      />
      {mode === "search" ? <SearchAdder mealId={mealId} /> : <RawAdder mealId={mealId} />}
    </div>
  );
}

function SearchAdder({ mealId }: { mealId: number }) {
  const [text, setText] = useState("");
  const [food, setFood] = useState<Food | null>(null);
  const [portion, setPortion] = useState<string>(GRAMS);
  const [qty, setQty] = useState("1");
  const [grams, setGrams] = useState("100");
  const recent = useRecentFoods();

  function pick(f: Food) {
    setFood(f);
    setText(f.name);
    const def = f.portions.find((p) => p.is_default) ?? f.portions[0];
    if (def) {
      setPortion(def.label);
      setQty("1");
    } else {
      setPortion(GRAMS);
      setGrams(String(f.default_grams ?? 100));
    }
  }

  const computedGrams =
    food && portion !== GRAMS
      ? (food.portions.find((p) => p.label === portion)?.grams ?? 0) * (Number(qty) || 0)
      : Number(grams) || 0;
  const preview = food ? macrosForGrams(food, computedGrams) : null;

  const mutation = useGatewayMutation({
    mutationFn: (item: MealItemAddIn) => addMealItems(mealId, [item]),
    update: (qc, meal) => qc.setQueryData(queryKeys.nutrition.meal(mealId), meal),
    invalidate: INVALIDATE,
    successMessage: "Item added",
    onSuccess: () => {
      setText("");
      setFood(null);
      setPortion(GRAMS);
      setQty("1");
      setGrams("100");
    },
  });

  function add() {
    let item: MealItemAddIn;
    if (food) {
      item =
        portion === GRAMS
          ? { food_id: food.id, grams: Number(grams) || 0 }
          : { food_id: food.id, portion_label: portion, qty: Number(qty) || 1 };
    } else if (text.trim()) {
      item = { food: text.trim(), grams: grams ? Number(grams) : undefined };
    } else {
      return;
    }
    mutation.mutate(item);
  }

  return (
    <div className="space-y-3">
      <FoodCombobox
        value={text}
        onChange={(t) => {
          setText(t);
          setFood(null);
        }}
        onPick={pick}
      />

      <div className="grid grid-cols-[1fr_auto] items-end gap-2">
        {food && food.portions.length > 0 ? (
          <Field id="portion" label="Serving">
            <select
              id="portion"
              value={portion}
              onChange={(e) => setPortion(e.target.value)}
              className="bg-background focus-visible:ring-ring h-9 w-full rounded-md border px-3 text-sm focus-visible:ring-2 focus-visible:outline-none"
            >
              {food.portions.map((p) => (
                <option key={p.label} value={p.label}>
                  {p.label} ({p.grams} g)
                </option>
              ))}
              <option value={GRAMS}>Custom grams</option>
            </select>
          </Field>
        ) : (
          <Field id="grams-only" label="Amount">
            <NumberInput
              id="grams-only"
              unit="g"
              value={grams}
              onChange={(e) => setGrams(e.target.value)}
            />
          </Field>
        )}

        {food && food.portions.length > 0 && portion !== GRAMS ? (
          <Field id="qty" label="Qty" className="w-20">
            <NumberInput id="qty" value={qty} step="0.5" onChange={(e) => setQty(e.target.value)} />
          </Field>
        ) : food && portion === GRAMS ? (
          <Field id="grams" label="Grams" className="w-24">
            <NumberInput
              id="grams"
              unit="g"
              value={grams}
              onChange={(e) => setGrams(e.target.value)}
            />
          </Field>
        ) : null}
      </div>

      <div className="flex items-center justify-between gap-2">
        <p className="text-muted-foreground text-sm tabular-nums">
          {preview ? `≈ ${formatMacros(preview)}` : text.trim() ? "Resolved on save" : ""}
        </p>
        <Button size="sm" onClick={add} loading={mutation.isPending} disabled={!text.trim()}>
          <Plus /> Add
        </Button>
      </div>

      <QueryState query={recent} loading={null}>
        {(foods) =>
          foods.length ? (
            <div className="flex flex-wrap gap-1.5 border-t pt-2">
              <span className="text-muted-foreground self-center text-xs">Recent:</span>
              {foods.slice(0, 8).map((f) => (
                <button
                  key={f.id}
                  type="button"
                  onClick={() => pick(f)}
                  className="hover:bg-accent rounded-full border px-2.5 py-0.5 text-xs"
                >
                  {f.name}
                </button>
              ))}
            </div>
          ) : (
            <></>
          )
        }
      </QueryState>
    </div>
  );
}

function RawAdder({ mealId }: { mealId: number }) {
  const form = useForm<RawItemForm, unknown, RawItemValues>({
    resolver: zodResolver(rawItemSchema),
    defaultValues: { food: "", kcal: "", protein_g: "", carbs_g: "", fat_g: "" },
  });
  const { register, handleSubmit, reset, formState } = form;

  const mutation = useGatewayMutation({
    mutationFn: (item: MealItemAddIn) => addMealItems(mealId, [item]),
    form,
    invalidate: [...INVALIDATE, queryKeys.nutrition.meal(mealId)],
    successMessage: "Item added",
    onSuccess: () => reset({ food: "", kcal: "", protein_g: "", carbs_g: "", fat_g: "" }),
  });

  const onSubmit = handleSubmit((v) =>
    mutation.mutate({
      food: v.food,
      kcal: v.kcal,
      protein_g: v.protein_g ?? null,
      carbs_g: v.carbs_g ?? null,
      fat_g: v.fat_g ?? null,
    }),
  );

  return (
    <form onSubmit={onSubmit} className="space-y-3">
      <Field id="raw-food" label="Item" error={formState.errors.food?.message}>
        <input
          id="raw-food"
          {...register("food")}
          placeholder="e.g. protein shake"
          className="bg-background focus-visible:ring-ring h-9 w-full rounded-md border px-3 text-sm focus-visible:ring-2 focus-visible:outline-none"
        />
      </Field>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Field id="raw-kcal" label="kcal" error={formState.errors.kcal?.message}>
          <NumberInput id="raw-kcal" placeholder="0" {...register("kcal")} />
        </Field>
        <Field id="raw-p" label="Protein" error={formState.errors.protein_g?.message}>
          <NumberInput id="raw-p" unit="g" placeholder="0" {...register("protein_g")} />
        </Field>
        <Field id="raw-c" label="Carbs" error={formState.errors.carbs_g?.message}>
          <NumberInput id="raw-c" unit="g" placeholder="0" {...register("carbs_g")} />
        </Field>
        <Field id="raw-f" label="Fat" error={formState.errors.fat_g?.message}>
          <NumberInput id="raw-f" unit="g" placeholder="0" {...register("fat_g")} />
        </Field>
      </div>
      <div className="flex justify-end">
        <Button type="submit" size="sm" loading={mutation.isPending}>
          <Plus /> Add
        </Button>
      </div>
    </form>
  );
}
