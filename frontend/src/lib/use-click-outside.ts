"use client";

import { useEffect, useRef } from "react";

/**
 * Calls `handler` on a pointer/focus event outside the returned ref element. Used by
 * the custom combobox to close its results dropdown. `enabled` gates the listener so it
 * isn't attached when the popup is closed.
 */
export function useClickOutside<T extends HTMLElement>(
  handler: () => void,
  enabled = true,
): React.RefObject<T | null> {
  const ref = useRef<T>(null);

  useEffect(() => {
    if (!enabled) return;
    const onPointer = (e: PointerEvent) => {
      const el = ref.current;
      if (el && !el.contains(e.target as Node)) handler();
    };
    document.addEventListener("pointerdown", onPointer);
    return () => document.removeEventListener("pointerdown", onPointer);
  }, [handler, enabled]);

  return ref;
}
