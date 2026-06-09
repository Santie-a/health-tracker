import { type NextRequest } from "next/server";

import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";

/** Recently-used foods for quick re-logging. */
export async function GET(request: NextRequest) {
  const limit = request.nextUrl.searchParams.get("limit");
  const query = limit ? { limit } : {};
  return respond(() => gw(gateway.GET("/api/v1/foods/recent", { params: { query } as never })));
}
