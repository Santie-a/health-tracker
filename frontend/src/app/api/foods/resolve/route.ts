import { NextResponse, type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";

/** Resolve a typed food name to a catalog entry via the shared matcher. */
export async function GET(request: NextRequest) {
  const name = request.nextUrl.searchParams.get("name");
  if (!name) {
    return NextResponse.json({ kind: "validation", detail: "name is required" }, { status: 400 });
  }
  return respond(() => gw(gateway.GET("/api/v1/foods/resolve", { params: { query: { name } } })));
}
