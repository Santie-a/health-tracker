import { NextResponse, type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";
import type { TrainingSetIn } from "@/lib/gateway/types";

/** Append sets to a training session. */
export async function POST(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const session_id = Number((await params).id);
  if (!Number.isInteger(session_id)) {
    return NextResponse.json({ kind: "validation", detail: "invalid id" }, { status: 400 });
  }
  const body = (await request.json()) as { sets: TrainingSetIn[] };
  return respond(() =>
    gw(
      gateway.POST("/api/v1/training/{session_id}/sets", {
        params: { path: { session_id } },
        body,
      }),
    ),
  );
}
