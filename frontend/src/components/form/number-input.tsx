import { forwardRef } from "react";

import { Input, type InputProps } from "@/components/ui/input";
import { cn } from "@/lib/utils";

/**
 * Numeric input with `inputMode="decimal"` (mobile number pad) and an optional trailing
 * unit adornment (kg, reps, m…). RHF registers it as a string; pair with a `z.coerce`
 * schema so the gateway receives a number.
 */
export const NumberInput = forwardRef<HTMLInputElement, InputProps & { unit?: string }>(
  ({ unit, className, ...props }, ref) => {
    if (!unit) {
      return <Input ref={ref} type="number" inputMode="decimal" className={className} {...props} />;
    }
    return (
      <div className="relative">
        <Input
          ref={ref}
          type="number"
          inputMode="decimal"
          className={cn("pr-10", className)}
          {...props}
        />
        <span className="text-muted-foreground pointer-events-none absolute inset-y-0 right-3 flex items-center text-sm">
          {unit}
        </span>
      </div>
    );
  },
);
NumberInput.displayName = "NumberInput";
