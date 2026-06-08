"use client";

import { ThemeProvider } from "next-themes";

import { Toaster } from "@/components/ui/toaster";
import { QueryProvider } from "@/lib/query/provider";

/**
 * Single client-side provider tree mounted once in the root layout: theme (system
 * default + manual toggle, class strategy) wrapping the TanStack Query cache, plus the
 * app-wide toaster for mutation feedback.
 */
export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      <QueryProvider>
        {children}
        <Toaster />
      </QueryProvider>
    </ThemeProvider>
  );
}
