import { QueryClient } from "@tanstack/react-query";

import { ApiError } from "./fetcher";

/**
 * Shared QueryClient defaults. Retries are deliberate, not blanket: only transient
 * failures (network/timeout/5xx, surfaced as a retryable `ApiError`) are retried, and
 * only once — a 404/422 is deterministic and retrying it just delays the error state.
 */
export function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        retry: (failureCount, error) =>
          error instanceof ApiError && error.retryable && failureCount < 1,
        refetchOnWindowFocus: true,
      },
      mutations: {
        retry: false,
      },
    },
  });
}
