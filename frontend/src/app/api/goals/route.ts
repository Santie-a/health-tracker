import { type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";
import type { GoalIn } from "@/lib/gateway/types";

/** List goals, optionally filtered by `status` (active|achieved|abandoned). */
export async function GET(request: NextRequest) {
  const sp = request.nextUrl.searchParams;
  const query: Record<string, string> = {};
  for (const k of ["status", "limit"]) {
    const v = sp.get(k);
    if (v) query[k] = v;
  }
  return respond(() => gw(gateway.GET("/api/v1/goals", { params: { query } as never })));
}

/** Create a goal. Unspecified fields are filled from the goal type server-side. */
export async function POST(request: NextRequest) {
  const body = (await request.json()) as GoalIn;
  return respond(() => gw(gateway.POST("/api/v1/goals", { body })));
}
