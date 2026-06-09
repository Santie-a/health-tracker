import { NextResponse, type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";
import type { MealIn } from "@/lib/gateway/types";

/** Day nutrition: meals + totals for a calendar date. */
export async function GET(request: NextRequest) {
  const date = request.nextUrl.searchParams.get("date");
  if (!date) {
    return NextResponse.json({ kind: "validation", detail: "date is required" }, { status: 400 });
  }
  return respond(() => gw(gateway.GET("/api/v1/meals", { params: { query: { date } } })));
}

/** Create a manual meal (items resolved server-side via nutrition_core). */
export async function POST(request: NextRequest) {
  const body = (await request.json()) as MealIn;
  return respond(() => gw(gateway.POST("/api/v1/meals", { body })));
}
