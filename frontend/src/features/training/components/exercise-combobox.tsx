"use client";

import { useQueryClient } from "@tanstack/react-query";
import { Check, Loader2, Plus } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Input } from "@/components/ui/input";
import type { Exercise } from "@/lib/gateway/types";
import { ApiError } from "@/lib/query/fetcher";
import { useClickOutside } from "@/lib/use-click-outside";
import { useDebouncedValue } from "@/lib/use-debounced-value";
import { cn } from "@/lib/utils";

import { createExercise } from "../api";
import { useExerciseSearch } from "../hooks";

/**
 * Search-as-you-type exercise picker. Free text is valid (the gateway resolves names to
 * the catalog server-side), so typing alone sets the value; the dropdown adds one-tap
 * selection of known exercises and an inline "quick-add" for a new one.
 */
export function ExerciseCombobox({
  value,
  onChange,
  invalid,
}: {
  value: string;
  onChange: (name: string) => void;
  invalid?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [adding, setAdding] = useState(false);
  const queryClient = useQueryClient();
  const debounced = useDebouncedValue(value.trim(), 250);
  const search = useExerciseSearch({ q: debounced, limit: 8 }, debounced.length >= 1);
  const containerRef = useClickOutside<HTMLDivElement>(() => setOpen(false), open);

  const results = search.data ?? [];
  const exactMatch = results.some((e) => e.name.toLowerCase() === value.trim().toLowerCase());
  const canQuickAdd = value.trim().length >= 2 && !exactMatch;

  function select(ex: Exercise) {
    onChange(ex.name);
    setOpen(false);
  }

  async function quickAdd() {
    const name = value.trim();
    if (!name) return;
    setAdding(true);
    try {
      const created = await createExercise({
        name,
        is_unilateral: false,
        is_bodyweight: false,
        muscles: [],
      });
      await queryClient.invalidateQueries({ queryKey: ["exercises"] });
      onChange(created.name);
      setOpen(false);
      toast.success(`Added "${created.name}"`);
    } catch (err) {
      // 409 = already exists; the free-text value still resolves server-side, so just close.
      if (err instanceof ApiError && err.status === 409) {
        setOpen(false);
      } else {
        toast.error(err instanceof ApiError ? err.friendly : "Couldn't add exercise");
      }
    } finally {
      setAdding(false);
    }
  }

  return (
    <div ref={containerRef} className="relative">
      <Input
        value={value}
        invalid={invalid}
        placeholder="Search exercise…"
        autoComplete="off"
        onChange={(e) => {
          onChange(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
      />
      {open && (results.length > 0 || canQuickAdd || search.isFetching) ? (
        <ul className="bg-popover absolute z-20 mt-1 max-h-60 w-full overflow-auto rounded-md border p-1 shadow-md">
          {search.isFetching && results.length === 0 ? (
            <li className="text-muted-foreground flex items-center gap-2 px-2 py-1.5 text-sm">
              <Loader2 className="size-3.5 animate-spin" /> Searching…
            </li>
          ) : null}
          {results.map((ex) => (
            <li key={ex.id}>
              <button
                type="button"
                onClick={() => select(ex)}
                className="hover:bg-accent flex w-full items-center justify-between gap-2 rounded px-2 py-1.5 text-left text-sm"
              >
                <span>
                  {ex.name}
                  {ex.primary_muscle ? (
                    <span className="text-muted-foreground"> · {ex.primary_muscle}</span>
                  ) : null}
                </span>
                {ex.name.toLowerCase() === value.trim().toLowerCase() ? (
                  <Check className="text-primary size-3.5" />
                ) : null}
              </button>
            </li>
          ))}
          {canQuickAdd ? (
            <li>
              <button
                type="button"
                onClick={quickAdd}
                disabled={adding}
                className={cn(
                  "hover:bg-accent flex w-full items-center gap-2 rounded px-2 py-1.5 text-left text-sm",
                  "text-primary disabled:opacity-50",
                )}
              >
                {adding ? (
                  <Loader2 className="size-3.5 animate-spin" />
                ) : (
                  <Plus className="size-3.5" />
                )}
                Add “{value.trim()}”
              </button>
            </li>
          ) : null}
        </ul>
      ) : null}
    </div>
  );
}
