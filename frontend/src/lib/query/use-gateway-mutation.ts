"use client";

import { useMutation, useQueryClient, type QueryKey } from "@tanstack/react-query";
import type { FieldValues, Path, UseFormReturn } from "react-hook-form";
import { toast } from "sonner";

import { ApiError } from "./fetcher";

/**
 * Wraps `useMutation` with the app's standard write-handling so every form behaves the
 * same way:
 *  - 422 validation → map each FastAPI field issue onto the RHF form (`setError`), so
 *    errors land on the right inputs instead of a generic banner.
 *  - everything else (network / 5xx / unexpected) → a friendly toast, never a crash.
 *  - on success → optional toast + invalidate the given query keys (e.g. dashboard).
 */
export function useGatewayMutation<TData, TVars, TForm extends FieldValues = FieldValues>(opts: {
  mutationFn: (vars: TVars) => Promise<TData>;
  form?: UseFormReturn<TForm>;
  successMessage?: string;
  invalidate?: QueryKey[];
  onSuccess?: (data: TData, vars: TVars) => void;
}) {
  const queryClient = useQueryClient();

  return useMutation<TData, Error, TVars>({
    mutationFn: opts.mutationFn,
    onSuccess: (data, vars) => {
      if (opts.successMessage) toast.success(opts.successMessage);
      for (const key of opts.invalidate ?? []) {
        void queryClient.invalidateQueries({ queryKey: key });
      }
      opts.onSuccess?.(data, vars);
    },
    onError: (error) => {
      if (error instanceof ApiError && error.kind === "validation" && opts.form) {
        const fieldErrors = error.fieldErrors();
        const entries = Object.entries(fieldErrors);
        if (entries.length) {
          for (const [field, message] of entries) {
            opts.form.setError(field as Path<TForm>, { type: "server", message });
          }
          return; // shown inline on the fields
        }
      }
      toast.error(error instanceof ApiError ? error.friendly : "Something went wrong.");
    },
  });
}
