import { NextResponse, type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";

/** BFF: aggregated day view. Forwards the `date` query to GET /api/v1/dashboard. */
export async function GET(request: NextRequest): Promise<NextResponse> {
  const date = request.nextUrl.searchParams.get("date");
  if (!date) {
    return NextResponse.json({ kind: "validation", detail: "date is required" }, { status: 400 });
  }
  return respond(() => gw(gateway.GET("/api/v1/dashboard", { params: { query: { date } } })));
}
