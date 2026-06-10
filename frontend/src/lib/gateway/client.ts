import "server-only";

import createClient from "openapi-fetch";

import { gatewayToken, gatewayUrl } from "@/lib/env";

import { fromResponse, fromThrown, GatewayError } from "./errors";
import type { paths } from "./types.gen";

/**
 * The ONLY module that knows the gateway URL + token. Server-only: it never ships
 * to the browser. Everything the app does against the gateway goes through here so
 * auth, timeouts, retries, and error normalization live in exactly one place.
 *
 * Transport policy (resilience): every request has a timeout and is retried ONCE on
 * a transient failure (network error, timeout, or 5xx) — never on a 4xx, which is a
 * deterministic client/validation error. Failures are surfaced as `GatewayError`,
 * never as raw fetch rejections or stack traces.
 */

const DEFAULT_TIMEOUT_MS = 30_000; // generous: photo meals proxy to the GPU service

function authHeaders(): Record<string, string> {
  const token = gatewayToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/** fetch with an abort-based timeout and a single retry on transient failures. */
async function resilientFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  let lastError: unknown;
  for (let attempt = 0; attempt < 2; attempt++) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
    try {
      const res = await fetch(input, { ...init, signal: controller.signal });
      if (res.status >= 500 && attempt === 0) {
        lastError = res; // 5xx → one retry, then return whatever we get
        continue;
      }
      return res;
    } catch (err) {
      lastError = err;
      if (attempt === 0) continue; // network/timeout → one retry
      throw err;
    } finally {
      clearTimeout(timer);
    }
  }
  if (lastError instanceof Response) return lastError;
  throw lastError;
}

/**
 * Lazily build the client so the gateway URL/token are read at REQUEST time, never at
 * module load: `next build` evaluates these route modules with no env present, and an
 * eager `gatewayUrl()` here would throw during "collect page data" (it has no runtime env).
 */
let cachedClient: ReturnType<typeof createClient<paths>> | undefined;

function getClient(): ReturnType<typeof createClient<paths>> {
  if (!cachedClient) {
    cachedClient = createClient<paths>({
      baseUrl: gatewayUrl(),
      headers: authHeaders(),
      fetch: resilientFetch,
    });
  }
  return cachedClient;
}

/**
 * Typed gateway client. Use with `gw()` to unwrap or throw a GatewayError. Backed by a
 * lazily-initialized client (see `getClient`) via a Proxy, so call sites stay
 * `gateway.GET(...)` while the env is only touched on first use.
 */
export const gateway = new Proxy({} as ReturnType<typeof createClient<paths>>, {
  get(_target, prop) {
    const real = getClient() as unknown as Record<string | symbol, unknown>;
    const value = real[prop];
    return typeof value === "function"
      ? (value as (...args: unknown[]) => unknown).bind(real)
      : value;
  },
});

type OpenApiResult<T> = {
  data?: T;
  error?: unknown;
  response: Response;
};

/**
 * Unwrap an openapi-fetch result into its data, or throw a normalized GatewayError.
 * Usage: `const day = await gw(gateway.GET("/api/v1/dashboard", { params: { query } }))`.
 */
export async function gw<T>(call: Promise<OpenApiResult<T>>): Promise<T> {
  let result: OpenApiResult<T>;
  try {
    result = await call;
  } catch (err) {
    throw fromThrown(err);
  }
  if (!result.response.ok || result.error !== undefined) {
    throw fromResponse(result.response.status, result.error ?? result.data);
  }
  return result.data as T;
}

/**
 * Raw authenticated passthrough to the gateway for endpoints the typed client is a
 * poor fit for (multipart uploads: photo meals, Samsung ingest). Applies the base URL,
 * auth header, timeout, and retry; returns the raw Response for the BFF to stream back.
 * Throws GatewayError only on transport failure (no response).
 */
export async function rawGatewayFetch(path: string, init?: RequestInit): Promise<Response> {
  const url = `${gatewayUrl()}${path.startsWith("/") ? path : `/${path}`}`;
  try {
    return await resilientFetch(url, {
      ...init,
      headers: { ...authHeaders(), ...(init?.headers as Record<string, string> | undefined) },
    });
  } catch (err) {
    throw fromThrown(err);
  }
}

export { GatewayError };
