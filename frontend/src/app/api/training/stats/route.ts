import { type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";

/** Strength balance stats over a range (defaults to the last 8 weeks server-side). */
export async function GET(request: NextRequest) {
  const sp = request.nextUrl.searchParams;
  const query: Record<string, string> = {};
  for (const k of ["from", "to"]) {
    const v = sp.get(k);
    if (v) query[k] = v;
  }
  return respond(() => gw(gateway.GET("/api/v1/training/stats", { params: { query } as never })));
}
