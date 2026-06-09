import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function NotFound() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-3 text-center">
      <p className="text-muted-foreground text-sm font-medium">404</p>
      <h1 className="text-lg font-semibold">Page not found</h1>
      <Link href="/" className={cn(buttonVariants({ variant: "outline" }))}>
        Back to Today
      </Link>
    </div>
  );
}
