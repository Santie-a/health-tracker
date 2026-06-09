import { type NextRequest } from "next/server";

import { proxyUpload } from "@/lib/gateway/bff";

/**
 * Samsung Health export import — streams the multipart upload (one or more CSVs under
 * the `files` field) straight to the gateway, which routes each file by its metadata
 * type. Import-only telemetry; never blocks manual logging.
 */
export async function POST(request: NextRequest) {
  return proxyUpload(request, "/api/v1/ingest/samsung");
}
