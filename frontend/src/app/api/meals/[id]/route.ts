import { NextResponse, type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";

/** Fetch one meal by id. */
export async function GET(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const meal_id = Number((await params).id);
  if (!Number.isInteger(meal_id)) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  return respond(() =>
    gw(gateway.GET("/api/v1/meals/{meal_id}", { params: { path: { meal_id } } })),
  );
}
