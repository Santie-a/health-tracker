import { cn } from "@/lib/utils";

/** Pulsing placeholder block. Compose several to mirror a widget's real layout. */
export function Skeleton({
  className,
  style,
}: {
  className?: string;
  style?: React.CSSProperties;
}) {
  return <div style={style} className={cn("bg-muted animate-pulse rounded-md", className)} />;
}
