import type { IngestResponse } from "@/lib/gateway/types";
import { apiSend } from "@/lib/query/fetcher";

/** Upload one or more Samsung export CSVs (multipart, repeated `files` field). */
export function uploadSamsung(files: File[]): Promise<IngestResponse> {
  const form = new FormData();
  for (const file of files) form.append("files", file);
  return apiSend<IngestResponse>("/api/ingest/samsung", { body: form });
}
