"use client";

import { useSyncExternalStore } from "react";

const noop = () => () => {};

/**
 * `false` during SSR / first render, `true` after the client takes over. Uses
 * `useSyncExternalStore` so it's lint-clean (no setState-in-effect) and SSR-safe.
 * Used to defer client-only widgets (e.g. Recharts' ResponsiveContainer, which needs a
 * measured DOM box) past hydration.
 */
export function useMounted(): boolean {
  return useSyncExternalStore(
    noop,
    () => true,
    () => false,
  );
}
