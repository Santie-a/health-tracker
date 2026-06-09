import { type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";
import type { TrainingSessionIn } from "@/lib/gateway/types";

/** List training sessions, optionally filtered by `type`/`from`/`to`. */
export async function GET(request: NextRequest) {
  const sp = request.nextUrl.searchParams;
  const query: Record<string, string> = {};
  for (const k of ["type", "from", "to", "limit"]) {
    const v = sp.get(k);
    if (v) query[k] = v;
  }
  return respond(() => gw(gateway.GET("/api/v1/training", { params: { query } as never })));
}

/** Create a training session (with optional inline sets). */
export async function POST(request: NextRequest) {
  const body = (await request.json()) as TrainingSessionIn;
  return respond(() => gw(gateway.POST("/api/v1/training", { body })));
}
