import { NextResponse, type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";

/** Force a regenerate + store of the day's recommendations. */
export async function POST(request: NextRequest) {
  const date = request.nextUrl.searchParams.get("date");
  if (!date) {
    return NextResponse.json({ kind: "validation", detail: "date is required" }, { status: 400 });
  }
  return respond(() =>
    gw(gateway.POST("/api/v1/recommendations/run", { params: { query: { date } } })),
  );
}
