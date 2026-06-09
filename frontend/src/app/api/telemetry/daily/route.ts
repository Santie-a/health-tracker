import { NextResponse, type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";

/** Daily rollup for one telemetry metric over a range. */
export async function GET(request: NextRequest) {
  const sp = request.nextUrl.searchParams;
  const metric = sp.get("metric");
  if (!metric) {
    return NextResponse.json({ kind: "validation", detail: "metric is required" }, { status: 400 });
  }
  const query: Record<string, string> = { metric };
  for (const k of ["from", "to"]) {
    const v = sp.get(k);
    if (v) query[k] = v;
  }
  return respond(() => gw(gateway.GET("/api/v1/telemetry/daily", { params: { query } as never })));
}
