import { forwardRef } from "react";

import { cn } from "@/lib/utils";

/** Form label. Plain element (no Radix) — pair with an input's `id` via `htmlFor`. */
export const Label = forwardRef<HTMLLabelElement, React.LabelHTMLAttributes<HTMLLabelElement>>(
  ({ className, ...props }, ref) => (
    <label
      ref={ref}
      className={cn("text-sm font-medium select-none peer-disabled:opacity-50", className)}
      {...props}
    />
  ),
);
Label.displayName = "Label";
