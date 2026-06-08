"use client";

import { ThemeProvider } from "next-themes";

import { QueryProvider } from "@/lib/query/provider";

/**
 * Single client-side provider tree mounted once in the root layout: theme (system
 * default + manual toggle, class strategy) wrapping the TanStack Query cache.
 */
export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      <QueryProvider>{children}</QueryProvider>
    </ThemeProvider>
  );
}
