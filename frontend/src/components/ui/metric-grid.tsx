import { cn } from "@/lib/utils";

/** Responsive grid for StatCards — 2 cols on phones, more as width allows. */
export function MetricGrid({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4", className)}>
      {children}
    </div>
  );
}
