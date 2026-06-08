"use client";

import { useTheme } from "next-themes";
import { Toaster as SonnerToaster } from "sonner";

/** App toaster, theme-synced with next-themes. Mounted once in Providers. */
export function Toaster() {
  const { resolvedTheme } = useTheme();
  return (
    <SonnerToaster
      theme={(resolvedTheme as "light" | "dark" | undefined) ?? "system"}
      position="top-right"
      richColors
      closeButton
    />
  );
}
