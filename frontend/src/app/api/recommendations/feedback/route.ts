import { type NextRequest } from "next/server";

import { respondNoContent } from "@/lib/gateway/bff";
import { gateway, gw } from "@/lib/gateway/client";
import type { FeedbackIn } from "@/lib/gateway/types";

/** Store day-level feedback for the recommendations. 404 if none are stored yet. */
export async function POST(request: NextRequest) {
  const body = (await request.json()) as FeedbackIn;
  return respondNoContent(() => gw(gateway.POST("/api/v1/recommendations/feedback", { body })));
}
