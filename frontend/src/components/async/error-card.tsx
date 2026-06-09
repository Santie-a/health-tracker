"use client";

import { RotateCw } from "lucide-react";

import { cn } from "@/lib/utils";

/**
 * Inline, contained error with a retry affordance. Used by `QueryState` and
 * `AsyncBoundary` so one failed widget shows here and the rest of the page survives.
 * Shows a user-safe message only — never a stack trace.
 */
export function ErrorCard({
  title = "Couldn't load this",
  message,
  onRetry,
  className,
}: {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}) {
  return (
    <div
      role="alert"
      className={cn(
        "border-destructive/40 bg-destructive/5 flex flex-col items-start gap-2 rounded-lg border p-4",
        className,
      )}
    >
      <p className="text-destructive text-sm font-medium">{title}</p>
      {message ? <p className="text-muted-foreground text-sm">{message}</p> : null}
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="hover:bg-accent mt-1 inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-sm font-medium transition-colors"
        >
          <RotateCw className="size-3.5" />
          Try again
        </button>
      ) : null}
    </div>
  );
}
