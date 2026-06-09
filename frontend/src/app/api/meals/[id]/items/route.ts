import { NextResponse, type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";
import type { AddItemsIn } from "@/lib/gateway/types";

/** Add items to a meal (catalog portion×qty, grams, free-text, or raw kcal). */
export async function POST(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const meal_id = Number((await params).id);
  if (!Number.isInteger(meal_id)) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  const body = (await request.json()) as AddItemsIn;
  return respond(() =>
    gw(gateway.POST("/api/v1/meals/{meal_id}/items", { params: { path: { meal_id } }, body })),
  );
}
