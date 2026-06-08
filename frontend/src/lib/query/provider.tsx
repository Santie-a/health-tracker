"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

import { makeQueryClient } from "./client";

/**
 * Client-side QueryClient provider. The client is created once per browser session
 * via lazy `useState` initializer (not at module scope) so it isn't shared across
 * requests during SSR.
 */
export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [client] = useState(makeQueryClient);
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
