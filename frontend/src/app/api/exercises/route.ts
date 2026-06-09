import { type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";
import type { ExerciseIn } from "@/lib/gateway/types";

/** Search the exercise catalog (`q`/`muscle`/`category`/`limit`). */
export async function GET(request: NextRequest) {
  const sp = request.nextUrl.searchParams;
  const query: Record<string, string> = {};
  for (const k of ["q", "muscle", "category", "limit"]) {
    const v = sp.get(k);
    if (v) query[k] = v;
  }
  return respond(() => gw(gateway.GET("/api/v1/exercises", { params: { query } as never })));
}

/** Create a custom exercise (409 if it already exists → surfaced to the form). */
export async function POST(request: NextRequest) {
  const body = (await request.json()) as ExerciseIn;
  return respond(() => gw(gateway.POST("/api/v1/exercises", { body })));
}
