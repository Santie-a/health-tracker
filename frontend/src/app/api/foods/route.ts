import { type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";

/** Search the foods catalog (`q`/`limit`). */
export async function GET(request: NextRequest) {
  const sp = request.nextUrl.searchParams;
  const query: Record<string, string> = {};
  for (const k of ["q", "limit"]) {
    const v = sp.get(k);
    if (v) query[k] = v;
  }
  return respond(() => gw(gateway.GET("/api/v1/foods", { params: { query } as never })));
}
