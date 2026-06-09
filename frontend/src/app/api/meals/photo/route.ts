import { type NextRequest } from "next/server";

import { proxyUpload } from "@/lib/gateway/bff";

/**
 * Photo meal entry — streams the multipart upload to the gateway, which proxies to the
 * GPU image-svc. If that box is offline the gateway returns a *degraded* empty manual
 * meal (201, `degraded: true`), never a 5xx, so the UI falls back to manual editing.
 */
export async function POST(request: NextRequest) {
  return proxyUpload(request, "/api/v1/meals/photo");
}
