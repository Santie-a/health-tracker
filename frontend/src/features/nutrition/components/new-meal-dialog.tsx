"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { format } from "date-fns";
import { Plus } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Field } from "@/components/form/field";
import { Button } from "@/components/ui/button";
import { Dialog, DialogClose, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import type { Meal, MealIn } from "@/lib/gateway/types";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";

import { createMeal } from "../api";
import { newMealSchema, type NewMealForm, type NewMealValues } from "../schemas";

const QUICK = ["Breakfast", "Lunch", "Dinner", "Snack"];

function nowLocalInput(): string {
  return format(new Date(), "yyyy-MM-dd'T'HH:mm");
}

/** Create an (empty) meal, then jump to its detail page to add items. */
export function NewMealDialog() {
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const form = useForm<NewMealForm, unknown, NewMealValues>({
    resolver: zodResolver(newMealSchema),
    defaultValues: { name: "", ts: nowLocalInput() },
  });
  const { register, handleSubmit, setValue, reset, formState } = form;

  const mutation = useGatewayMutation({
    mutationFn: createMeal,
    form,
    invalidate: [["nutrition"], ["dashboard"]],
    onSuccess: (meal: Meal) => {
      setOpen(false);
      reset({ name: "", ts: nowLocalInput() });
      router.push(`/nutrition/${meal.id}`);
    },
  });

  const onSubmit = handleSubmit((v) => {
    const body: MealIn = { ts: new Date(v.ts).toISOString(), name: v.name || null, items: [] };
    mutation.mutate(body);
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Plus /> Log meal
        </Button>
      </DialogTrigger>
      <DialogContent title="Log a meal" description="Name it, then add items on the next screen.">
        <form onSubmit={onSubmit} className="space-y-4">
          <div className="flex flex-wrap gap-1.5">
            {QUICK.map((q) => (
              <button
                key={q}
                type="button"
                onClick={() => setValue("name", q)}
                className="hover:bg-accent rounded-full border px-2.5 py-1 text-xs font-medium"
              >
                {q}
              </button>
            ))}
          </div>
          <Field id="meal-name" label="Name" error={formState.errors.name?.message}>
            <Input id="meal-name" placeholder="optional" {...register("name")} />
          </Field>
          <Field id="meal-ts" label="When" error={formState.errors.ts?.message}>
            <Input id="meal-ts" type="datetime-local" {...register("ts")} />
          </Field>
          <div className="flex justify-end gap-2">
            <DialogClose asChild>
              <Button type="button" variant="ghost">
                Cancel
              </Button>
            </DialogClose>
            <Button type="submit" loading={mutation.isPending}>
              Create
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
