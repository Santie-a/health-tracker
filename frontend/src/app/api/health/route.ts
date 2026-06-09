import { NextResponse } from "next/server";

import { rawGatewayFetch } from "@/lib/gateway/client";
import { GatewayError } from "@/lib/gateway/errors";

/**
 * BFF connectivity check. Confirms the frontend can reach the gateway with its
 * configured token, surfacing the gateway's readiness without coupling the page to
 * it. Always answers 200 with a status object (degraded/unreachable are data, not
 * errors) so a dashboard widget can render the connection state instead of crashing.
 */
export async function GET(): Promise<NextResponse> {
  try {
    const res = await rawGatewayFetch("/health/ready");
    const body = (await res.json().catch(() => null)) as { database?: boolean } | null;
    return NextResponse.json({
      ok: res.ok,
      gateway: res.ok ? "ready" : "degraded",
      database: body?.database ?? null,
    });
  } catch (err) {
    const reason = err instanceof GatewayError ? err.friendly : "unreachable";
    return NextResponse.json({ ok: false, gateway: "unreachable", reason });
  }
}
