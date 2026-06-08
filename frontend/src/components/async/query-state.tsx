"use client";

import type { UseQueryResult } from "@tanstack/react-query";
import type { ReactNode } from "react";

import { ApiError } from "@/lib/query/fetcher";

import { EmptyState } from "./empty-state";
import { ErrorCard } from "./error-card";
import { Skeleton } from "./skeleton";

/**
 * The default way every data widget renders a TanStack Query result: explicit
 * loading → error → empty → data. Enforces the rule that no view assumes data exists.
 *
 * - `loading` defaults to a skeleton; pass a layout-matched one for less jank.
 * - `isEmpty` lets a successful-but-empty response render `empty` instead of children.
 * - errors show a contained `ErrorCard` with a retry wired to `query.refetch`.
 */
export function QueryState<T>({
  query,
  children,
  loading,
  empty,
  isEmpty,
  errorTitle,
}: {
  query: UseQueryResult<T>;
  children: (data: T) => ReactNode;
  loading?: ReactNode;
  empty?: ReactNode;
  isEmpty?: (data: T) => boolean;
  errorTitle?: string;
}) {
  if (query.isPending) {
    return <>{loading ?? <Skeleton className="h-24 w-full" />}</>;
  }

  if (query.isError) {
    const message =
      query.error instanceof ApiError ? query.error.friendly : "Something went wrong.";
    return <ErrorCard title={errorTitle} message={message} onRetry={() => query.refetch()} />;
  }

  const data = query.data;
  if (isEmpty?.(data)) {
    return <>{empty ?? <EmptyState />}</>;
  }

  return <>{children(data)}</>;
}
