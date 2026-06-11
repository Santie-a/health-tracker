import { NextResponse, type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";
import type { MealItemUpdate } from "@/lib/gateway/types";

function parseIds(meal: string, item: string): { meal_id: number; item_id: number } | null {
  const meal_id = Number(meal);
  const item_id = Number(item);
  if (!Number.isInteger(meal_id) || !Number.isInteger(item_id)) return null;
  return { meal_id, item_id };
}

/** Edit one meal item (returns the updated meal). */
export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string; itemId: string }> },
) {
  const p = await params;
  const ids = parseIds(p.id, p.itemId);
  if (ids === null) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  const body = (await request.json()) as MealItemUpdate;
  return respond(() =>
    gw(
      gateway.PATCH("/api/v1/meals/{meal_id}/items/{item_id}", {
        params: { path: ids },
        body,
      }),
    ),
  );
}

/** Remove one meal item (returns the updated meal). */
export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string; itemId: string }> },
) {
  const p = await params;
  const ids = parseIds(p.id, p.itemId);
  if (ids === null) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  return respond(() =>
    gw(gateway.DELETE("/api/v1/meals/{meal_id}/items/{item_id}", { params: { path: ids } })),
  );
}
