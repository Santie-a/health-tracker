import { NextResponse, type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";
import type { TrainingSetUpdate } from "@/lib/gateway/types";

function parseIds(
  session: string,
  set: string,
): { session_id: number; set_id: number } | null {
  const session_id = Number(session);
  const set_id = Number(set);
  if (!Number.isInteger(session_id) || !Number.isInteger(set_id)) return null;
  return { session_id, set_id };
}

/** Edit one set (returns the updated session). */
export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string; setId: string }> },
) {
  const p = await params;
  const ids = parseIds(p.id, p.setId);
  if (ids === null) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  const body = (await request.json()) as TrainingSetUpdate;
  return respond(() =>
    gw(
      gateway.PATCH("/api/v1/training/{session_id}/sets/{set_id}", {
        params: { path: ids },
        body,
      }),
    ),
  );
}

/** Remove one set (returns the updated session). */
export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string; setId: string }> },
) {
  const p = await params;
  const ids = parseIds(p.id, p.setId);
  if (ids === null) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  return respond(() =>
    gw(gateway.DELETE("/api/v1/training/{session_id}/sets/{set_id}", { params: { path: ids } })),
  );
}
