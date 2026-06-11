import { NextResponse, type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";
import type { ExerciseUpdate } from "@/lib/gateway/types";

function parseId(raw: string): number | null {
  const id = Number(raw);
  return Number.isInteger(id) ? id : null;
}

/** Edit a catalog exercise (409 if a rename collides → surfaced to the form). */
export async function PATCH(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const exercise_id = parseId((await params).id);
  if (exercise_id === null) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  const body = (await request.json()) as ExerciseUpdate;
  return respond(() =>
    gw(gateway.PATCH("/api/v1/exercises/{exercise_id}", { params: { path: { exercise_id } }, body })),
  );
}

/** Delete a catalog exercise (soft-deletes when logged sets still reference it). */
export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const exercise_id = parseId((await params).id);
  if (exercise_id === null) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  return respond(() =>
    gw(gateway.DELETE("/api/v1/exercises/{exercise_id}", { params: { path: { exercise_id } } })),
  );
}
