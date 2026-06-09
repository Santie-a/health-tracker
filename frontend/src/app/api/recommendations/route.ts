import { NextResponse, type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";

/** The day's recommendations (lazy-generated + stored on first request). */
export async function GET(request: NextRequest) {
  const date = request.nextUrl.searchParams.get("date");
  if (!date) {
    return NextResponse.json({ kind: "validation", detail: "date is required" }, { status: 400 });
  }
  return respond(() => gw(gateway.GET("/api/v1/recommendations", { params: { query: { date } } })));
}
