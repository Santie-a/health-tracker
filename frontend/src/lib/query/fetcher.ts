import type { GatewayErrorKind, ValidationIssue } from "@/lib/gateway/errors";

/**
 * Browser-side fetch wrapper over the BFF (`/api/*`). It speaks only to our own
 * origin — never the gateway directly — and turns the BFF's normalized error body
 * (`{ kind, detail, request_id }`) back into a typed `ApiError` so hooks and forms
 * can branch on `kind` (retry a network blip, map 422 issues to fields, etc.).
 */

export class ApiError extends Error {
  readonly status: number;
  readonly kind: GatewayErrorKind;
  readonly issues?: ValidationIssue[];
  readonly requestId?: string;

  constructor(
    status: number,
    kind: GatewayErrorKind,
    message: string,
    opts?: {
      issues?: ValidationIssue[];
      requestId?: string;
    },
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.kind = kind;
    this.issues = opts?.issues;
    this.requestId = opts?.requestId;
  }

  get retryable(): boolean {
    return this.kind === "network" || this.kind === "timeout" || this.kind === "server";
  }

  get friendly(): string {
    switch (this.kind) {
      case "network":
      case "timeout":
        return "Can't reach the server. Check your connection and try again.";
      case "unauthorized":
        return "Not authorized.";
      case "validation":
        return this.issues?.[0]?.msg ?? "Some fields are invalid.";
      case "server":
        return "The server hit an error. Please try again.";
      default:
        return this.message || "Something went wrong.";
    }
  }

  /** FastAPI 422 `loc` → message map, keyed by the last field segment, for forms. */
  fieldErrors(): Record<string, string> {
    const out: Record<string, string> = {};
    for (const issue of this.issues ?? []) {
      const field = issue.loc.filter((p) => typeof p === "string").at(-1);
      if (field && field !== "body" && !(field in out)) out[String(field)] = issue.msg;
    }
    return out;
  }
}

function inferKind(status: number): GatewayErrorKind {
  if (status === 0) return "network";
  if (status === 401 || status === 403) return "unauthorized";
  if (status === 404) return "not_found";
  if (status === 422) return "validation";
  if (status >= 500) return "server";
  if (status >= 400) return "client";
  return "unknown";
}

async function parse<T>(res: Response): Promise<T> {
  if (res.status === 204) return undefined as T;
  const body = (await res.json().catch(() => null)) as {
    kind?: GatewayErrorKind;
    detail?: string | ValidationIssue[];
    request_id?: string;
  } | null;
  if (res.ok) return body as T;

  const issues = Array.isArray(body?.detail) ? body.detail : undefined;
  const message =
    typeof body?.detail === "string"
      ? body.detail
      : (issues?.[0]?.msg ?? `Request failed (${res.status})`);
  throw new ApiError(res.status, body?.kind ?? inferKind(res.status), message, {
    issues,
    requestId: body?.request_id,
  });
}

function withQuery(path: string, query?: Record<string, string | number | undefined>): string {
  if (!query) return path;
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(query)) {
    if (v !== undefined && v !== "") sp.set(k, String(v));
  }
  const qs = sp.toString();
  return qs ? `${path}?${qs}` : path;
}

export async function apiGet<T>(
  path: string,
  query?: Record<string, string | number | undefined>,
): Promise<T> {
  try {
    // no-store: React Query owns caching; the browser HTTP cache must not serve a
    // stale list after a mutation (the "must refresh to see it" bug).
    return await parse<T>(await fetch(withQuery(path, query), { cache: "no-store" }));
  } catch (err) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(0, "network", "Network error");
  }
}

export async function apiSend<T>(
  path: string,
  init: {
    method?: string;
    json?: unknown;
    body?: BodyInit;
    query?: Record<string, string | number | undefined>;
  } = {},
): Promise<T> {
  const { method = "POST", json, body, query } = init;
  try {
    const res = await fetch(withQuery(path, query), {
      method,
      headers: json !== undefined ? { "content-type": "application/json" } : undefined,
      body: json !== undefined ? JSON.stringify(json) : body,
    });
    return await parse<T>(res);
  } catch (err) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(0, "network", "Network error");
  }
}
