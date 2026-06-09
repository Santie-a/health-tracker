import "server-only";

import { NextResponse } from "next/server";

import { rawGatewayFetch } from "./client";
import { GatewayError } from "./errors";

/**
 * Helpers shared by the per-domain BFF route handlers (`app/api/*`). Each handler
 * stays thin: read inputs, call the typed gateway client, hand the result to one of
 * these. They guarantee the browser only ever sees a clean JSON body + status — never
 * a stack trace, never an unhandled rejection that 500s the Node process.
 *
 * Every response is marked `no-store`: the BFF proxies *live* data, so the browser must
 * never serve a cached body after a mutation (otherwise a logged session/meal wouldn't
 * appear until a hard refresh). React Query is the only cache layer that should apply.
 */

const NO_STORE = { "cache-control": "no-store" } as const;

function errorResponse(err: unknown): NextResponse {
  const ge =
    err instanceof GatewayError
      ? err
      : new GatewayError({ kind: "unknown", status: 500, message: "Unexpected BFF error" });
  // 0 = no HTTP response (network/timeout) → 502 Bad Gateway to the browser.
  const status = ge.status && ge.status >= 400 ? ge.status : 502;
  return NextResponse.json(ge.toBody(), { status, headers: NO_STORE });
}

/** Run a typed gateway call and return its data as JSON, or a normalized error. */
export async function respond<T>(fn: () => Promise<T>): Promise<NextResponse> {
  try {
    return NextResponse.json(await fn(), { headers: NO_STORE });
  } catch (err) {
    return errorResponse(err);
  }
}

/** Like `respond`, but for gateway endpoints that return 204 No Content. */
export async function respondNoContent(fn: () => Promise<unknown>): Promise<NextResponse> {
  try {
    await fn();
    return new NextResponse(null, { status: 204, headers: NO_STORE });
  } catch (err) {
    return errorResponse(err);
  }
}

/**
 * Stream a multipart/binary upload straight through to the gateway (photo meals,
 * Samsung ingest) and relay the gateway's JSON response. Preserves the original
 * Content-Type (so the multipart boundary survives) and adds auth server-side.
 */
export async function proxyUpload(request: Request, gatewayPath: string): Promise<NextResponse> {
  try {
    const body = await request.arrayBuffer();
    const contentType = request.headers.get("content-type");
    const res = await rawGatewayFetch(gatewayPath, {
      method: request.method,
      body,
      headers: contentType ? { "content-type": contentType } : undefined,
    });
    const payload = await res.text();
    return new NextResponse(payload, {
      status: res.status,
      headers: {
        "content-type": res.headers.get("content-type") ?? "application/json",
        ...NO_STORE,
      },
    });
  } catch (err) {
    return errorResponse(err);
  }
}
