/**
 * One normalized error envelope for everything that can go wrong talking to the
 * gateway, so the BFF and the UI never have to branch on raw fetch/HTTP shapes.
 *
 * The gateway returns `{ detail, request_id }` on errors (see server core/errors.py);
 * `detail` may be a string or FastAPI's 422 validation array. We capture both plus a
 * `kind` so callers can decide intent (retry a network blip, show field errors on 422,
 * surface the manual-entry path on a degraded integration, etc.).
 */

export type GatewayErrorKind =
  | "network" // no response (DNS, refused, timeout, fetch threw)
  | "timeout"
  | "unauthorized" // 401/403
  | "not_found" // 404
  | "validation" // 422
  | "server" // 5xx
  | "client" // other 4xx
  | "unknown";

/** FastAPI 422 item: `{ loc, msg, type }`. */
export interface ValidationIssue {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface GatewayErrorBody {
  detail?: string | ValidationIssue[];
  request_id?: string;
}

export class GatewayError extends Error {
  readonly kind: GatewayErrorKind;
  readonly status: number; // 0 when there was no HTTP response
  readonly requestId?: string;
  readonly issues?: ValidationIssue[];

  constructor(opts: {
    kind: GatewayErrorKind;
    status: number;
    message: string;
    requestId?: string;
    issues?: ValidationIssue[];
    cause?: unknown;
  }) {
    super(opts.message, { cause: opts.cause });
    this.name = "GatewayError";
    this.kind = opts.kind;
    this.status = opts.status;
    this.requestId = opts.requestId;
    this.issues = opts.issues;
  }

  /** A short, user-safe message — never a stack trace. */
  get friendly(): string {
    switch (this.kind) {
      case "network":
      case "timeout":
        return "Can't reach the server. Check your connection and try again.";
      case "unauthorized":
        return "Not authorized. The gateway token may be missing or wrong.";
      case "not_found":
        return "Not found.";
      case "validation":
        return this.issues?.[0]?.msg ?? "Some fields are invalid.";
      case "server":
        return "The server hit an error. Please try again.";
      default:
        return this.message || "Something went wrong.";
    }
  }

  /** Network/5xx are worth a single retry; client errors are not. */
  get retryable(): boolean {
    return this.kind === "network" || this.kind === "timeout" || this.kind === "server";
  }

  /** Shape sent back through the BFF to the browser (no internals leaked). */
  toBody(): GatewayErrorBody & { kind: GatewayErrorKind } {
    return {
      kind: this.kind,
      detail: this.issues ?? this.message,
      request_id: this.requestId,
    };
  }
}

function kindForStatus(status: number): GatewayErrorKind {
  if (status === 401 || status === 403) return "unauthorized";
  if (status === 404) return "not_found";
  if (status === 422) return "validation";
  if (status >= 500) return "server";
  if (status >= 400) return "client";
  return "unknown";
}

/** Build a GatewayError from a non-2xx HTTP response + parsed body. */
export function fromResponse(status: number, body: unknown): GatewayError {
  const kind = kindForStatus(status);
  const b = (body ?? {}) as GatewayErrorBody;
  const issues = Array.isArray(b.detail) ? b.detail : undefined;
  const message =
    typeof b.detail === "string" ? b.detail : issues?.[0]?.msg ? issues[0].msg : `HTTP ${status}`;
  return new GatewayError({ kind, status, message, requestId: b.request_id, issues });
}

/** Build a GatewayError from a thrown fetch/abort error (no HTTP response). */
export function fromThrown(err: unknown): GatewayError {
  const isAbort = err instanceof Error && err.name === "AbortError";
  return new GatewayError({
    kind: isAbort ? "timeout" : "network",
    status: 0,
    message: err instanceof Error ? err.message : "Network error",
    cause: err,
  });
}
