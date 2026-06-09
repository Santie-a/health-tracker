import { NextResponse, type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";

/** Fetch one training session by id. */
export async function GET(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const session_id = Number((await params).id);
  if (!Number.isInteger(session_id)) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  return respond(() =>
    gw(gateway.GET("/api/v1/training/{session_id}", { params: { path: { session_id } } })),
  );
}
