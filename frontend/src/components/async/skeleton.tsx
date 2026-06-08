import { cn } from "@/lib/utils";

/** Pulsing placeholder block. Compose several to mirror a widget's real layout. */
export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("bg-muted animate-pulse rounded-md", className)} />;
}
