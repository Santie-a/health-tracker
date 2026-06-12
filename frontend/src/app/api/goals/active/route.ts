import { respond } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";

/** The active goal(s) (at most one body + one sleep) with live progress. */
export async function GET() {
  return respond(() => gw(gateway.GET("/api/v1/goals/active")));
}
