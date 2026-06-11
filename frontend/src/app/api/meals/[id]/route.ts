import { NextResponse, type NextRequest } from "next/server";

import { respond, respondNoContent } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";
import type { MealUpdate } from "@/lib/gateway/types";

function parseId(raw: string): number | null {
  const id = Number(raw);
  return Number.isInteger(id) ? id : null;
}

/** Fetch one meal by id. */
export async function GET(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const meal_id = parseId((await params).id);
  if (meal_id === null) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  return respond(() =>
    gw(gateway.GET("/api/v1/meals/{meal_id}", { params: { path: { meal_id } } })),
  );
}

/** Edit a meal's name and/or timestamp. */
export async function PATCH(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const meal_id = parseId((await params).id);
  if (meal_id === null) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  const body = (await request.json()) as MealUpdate;
  return respond(() =>
    gw(gateway.PATCH("/api/v1/meals/{meal_id}", { params: { path: { meal_id } }, body })),
  );
}

/** Delete a meal (cascades to its items). */
export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const meal_id = parseId((await params).id);
  if (meal_id === null) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  return respondNoContent(() =>
    gw(gateway.DELETE("/api/v1/meals/{meal_id}", { params: { path: { meal_id } } })),
  );
}
