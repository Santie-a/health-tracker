"use client";

import { RotateCw } from "lucide-react";
import { useEffect } from "react";

import { Button } from "@/components/ui/button";

/**
 * Route-level error boundary (Next convention). Catches render/data errors a view's own
 * `AsyncBoundary`/`QueryState` didn't, so the user gets a calm retry instead of a blank
 * page. Logs to the console for a client-side breadcrumb.
 */
export default function RouteError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Route error:", error);
  }, [error]);

  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-3 text-center">
      <h1 className="text-lg font-semibold">Something went wrong</h1>
      <p className="text-muted-foreground max-w-sm text-sm">
        This view hit an unexpected error. Your data is safe — try again.
      </p>
      <Button onClick={reset}>
        <RotateCw /> Try again
      </Button>
    </div>
  );
}
