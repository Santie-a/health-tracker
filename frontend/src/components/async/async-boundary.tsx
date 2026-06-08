"use client";

import { Component, type ReactNode, Suspense } from "react";

import { ApiError } from "@/lib/query/fetcher";

import { ErrorCard } from "./error-card";
import { Skeleton } from "./skeleton";

/**
 * Per-widget safety net for *render-time* errors (a child threw while rendering). Pair
 * with `QueryState` (which handles async fetch states): QueryState covers the request,
 * this boundary covers everything else so a single broken widget can't blank the page.
 */
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, reset: () => void) => ReactNode;
}

interface ErrorBoundaryState {
  error: Error | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error) {
    // Client-side breadcrumb; server-side errors are already logged by the gateway/BFF.
    console.error("Widget error boundary caught:", error);
  }

  reset = () => this.setState({ error: null });

  render() {
    const { error } = this.state;
    if (error) {
      if (this.props.fallback) return this.props.fallback(error, this.reset);
      const message = error instanceof ApiError ? error.friendly : "Something went wrong.";
      return <ErrorCard message={message} onRetry={this.reset} />;
    }
    return this.props.children;
  }
}

/** Suspense + error boundary in one. Wrap any self-contained data widget. */
export function AsyncBoundary({
  children,
  pending,
  fallback,
}: {
  children: ReactNode;
  pending?: ReactNode;
  fallback?: (error: Error, reset: () => void) => ReactNode;
}) {
  return (
    <ErrorBoundary fallback={fallback}>
      <Suspense fallback={pending ?? <Skeleton className="h-24 w-full" />}>{children}</Suspense>
    </ErrorBoundary>
  );
}
