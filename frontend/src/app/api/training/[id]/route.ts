import { NextResponse, type NextRequest } from "next/server";

import { respond, respondNoContent } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";
import type { TrainingSessionUpdate } from "@/lib/gateway/types";

function parseId(raw: string): number | null {
  const id = Number(raw);
  return Number.isInteger(id) ? id : null;
}

/** Fetch one training session by id. */
export async function GET(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const session_id = parseId((await params).id);
  if (session_id === null) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  return respond(() =>
    gw(gateway.GET("/api/v1/training/{session_id}", { params: { path: { session_id } } })),
  );
}

/** Edit a session's fields (load recomputes from duration×rpe server-side). */
export async function PATCH(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const session_id = parseId((await params).id);
  if (session_id === null) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  const body = (await request.json()) as TrainingSessionUpdate;
  return respond(() =>
    gw(gateway.PATCH("/api/v1/training/{session_id}", { params: { path: { session_id } }, body })),
  );
}

/** Delete a training session (cascades to its sets). */
export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const session_id = parseId((await params).id);
  if (session_id === null) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  return respondNoContent(() =>
    gw(gateway.DELETE("/api/v1/training/{session_id}", { params: { path: { session_id } } })),
  );
}
