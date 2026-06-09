"use client";

import { Loader2 } from "lucide-react";
import { useState } from "react";

import { Input } from "@/components/ui/input";
import type { Food } from "@/lib/gateway/types";
import { useClickOutside } from "@/lib/use-click-outside";
import { useDebouncedValue } from "@/lib/use-debounced-value";

import { useFoodSearch } from "../hooks";

/**
 * Search-as-you-type food picker. Free text is valid (the gateway resolves names to the
 * catalog with grams), but picking a catalog food via `onPick` unlocks the serving
 * picker (portions + per-100g macros) for a live preview.
 */
export function FoodCombobox({
  value,
  onChange,
  onPick,
  invalid,
  placeholder = "Search food…",
}: {
  value: string;
  onChange: (text: string) => void;
  onPick: (food: Food) => void;
  invalid?: boolean;
  placeholder?: string;
}) {
  const [open, setOpen] = useState(false);
  const debounced = useDebouncedValue(value.trim(), 250);
  const search = useFoodSearch(debounced, debounced.length >= 1);
  const ref = useClickOutside<HTMLDivElement>(() => setOpen(false), open);
  const results = search.data ?? [];

  return (
    <div ref={ref} className="relative">
      <Input
        value={value}
        invalid={invalid}
        placeholder={placeholder}
        autoComplete="off"
        onChange={(e) => {
          onChange(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
      />
      {open && (results.length > 0 || search.isFetching) ? (
        <ul className="bg-popover absolute z-20 mt-1 max-h-60 w-full overflow-auto rounded-md border p-1 shadow-md">
          {search.isFetching && results.length === 0 ? (
            <li className="text-muted-foreground flex items-center gap-2 px-2 py-1.5 text-sm">
              <Loader2 className="size-3.5 animate-spin" /> Searching…
            </li>
          ) : null}
          {results.map((food) => (
            <li key={food.id}>
              <button
                type="button"
                onClick={() => {
                  onPick(food);
                  setOpen(false);
                }}
                className="hover:bg-accent flex w-full items-center justify-between gap-2 rounded px-2 py-1.5 text-left text-sm"
              >
                <span>{food.name}</span>
                {food.kcal_100g != null ? (
                  <span className="text-muted-foreground text-xs">
                    {Math.round(food.kcal_100g)} kcal/100g
                  </span>
                ) : null}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
