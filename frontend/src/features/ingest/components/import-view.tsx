"use client";

import { FileUp, Upload, X } from "lucide-react";
import { useRef, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { SectionCard } from "@/components/ui/section-card";
import type { IngestResponse } from "@/lib/gateway/types";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";
import { cn } from "@/lib/utils";

import { uploadSamsung } from "../api";

function fmtBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1_048_576) return `${(n / 1024).toFixed(0)} KB`;
  return `${(n / 1_048_576).toFixed(1)} MB`;
}

export function ImportView() {
  const [files, setFiles] = useState<File[]>([]);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const mutation = useGatewayMutation({
    mutationFn: uploadSamsung,
    // New telemetry → refresh everything that reads it.
    invalidate: [["dashboard"], ["telemetry"], ["recommendations"]],
    onSuccess: (res) => {
      toast.success(`Imported ${res.written.toLocaleString()} rows from ${res.files.length} files`);
      setFiles([]);
    },
  });

  function addFiles(list: FileList | null) {
    if (!list) return;
    setFiles((prev) => [...prev, ...Array.from(list)]);
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Import</h1>
        <p className="text-muted-foreground text-sm">
          Upload your Samsung Health export CSVs (the <code>com.samsung.*</code> files). Include the{" "}
          <code>sleep_stage</code> file alongside <code>sleep</code> to enrich deep/awake minutes.
          Re-uploading the same export is safe — imports are idempotent.
        </p>
      </div>

      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          addFiles(e.dataTransfer.files);
        }}
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border border-dashed p-10 text-center transition-colors",
          dragging ? "border-primary bg-primary/5" : "hover:bg-accent/40",
        )}
      >
        <FileUp className="text-muted-foreground size-6" />
        <p className="text-sm font-medium">Drop CSV files here, or click to browse</p>
        <p className="text-muted-foreground text-xs">Multiple files at once</p>
        <input
          ref={inputRef}
          type="file"
          accept=".csv,text/csv"
          multiple
          className="hidden"
          onChange={(e) => {
            addFiles(e.target.files);
            e.target.value = "";
          }}
        />
      </div>

      {files.length > 0 ? (
        <div className="space-y-2">
          <ul className="divide-y rounded-xl border">
            {files.map((f, i) => (
              <li key={`${f.name}-${i}`} className="flex items-center gap-3 p-2.5 text-sm">
                <FileUp className="text-muted-foreground size-4 shrink-0" />
                <span className="min-w-0 flex-1 truncate">{f.name}</span>
                <span className="text-muted-foreground shrink-0 text-xs">{fmtBytes(f.size)}</span>
                <button
                  type="button"
                  aria-label={`Remove ${f.name}`}
                  onClick={() => setFiles((prev) => prev.filter((_, j) => j !== i))}
                  className="text-muted-foreground hover:text-foreground shrink-0"
                >
                  <X className="size-4" />
                </button>
              </li>
            ))}
          </ul>
          <div className="flex justify-end">
            <Button loading={mutation.isPending} onClick={() => mutation.mutate(files)}>
              <Upload /> Import {files.length} file{files.length === 1 ? "" : "s"}
            </Button>
          </div>
        </div>
      ) : null}

      {mutation.data ? <ImportReport report={mutation.data} /> : null}
    </div>
  );
}

function ImportReport({ report }: { report: IngestResponse }) {
  return (
    <SectionCard title="Import report">
      <div className="mb-3 flex flex-wrap gap-2">
        <Badge variant="success">{report.written.toLocaleString()} written</Badge>
        <Badge>{report.parsed.toLocaleString()} parsed</Badge>
        {report.skipped > 0 ? (
          <Badge variant="warning">{report.skipped.toLocaleString()} skipped</Badge>
        ) : null}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-muted-foreground text-left text-xs">
              <th className="py-1.5 font-medium">File</th>
              <th className="py-1.5 font-medium">Target</th>
              <th className="py-1.5 text-right font-medium">Parsed</th>
              <th className="py-1.5 text-right font-medium">Written</th>
              <th className="py-1.5 text-right font-medium">Skipped</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {report.files.map((f, i) => (
              <tr key={`${f.filename}-${i}`}>
                <td className="max-w-[16rem] truncate py-1.5" title={f.filename}>
                  {f.filename}
                </td>
                <td className="text-muted-foreground py-1.5">{f.target ?? f.data_type ?? "—"}</td>
                <td className="py-1.5 text-right tabular-nums">{f.parsed}</td>
                <td className="py-1.5 text-right tabular-nums">{f.written}</td>
                <td className="py-1.5 text-right tabular-nums">{f.skipped || ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {report.files.some((f) => f.errors.length) ? (
        <div className="mt-3 space-y-1">
          {report.files
            .filter((f) => f.errors.length)
            .map((f, i) => (
              <details key={i} className="text-xs">
                <summary className="text-warning cursor-pointer">
                  {f.filename}: {f.errors.length} issue{f.errors.length === 1 ? "" : "s"}
                </summary>
                <ul className="text-muted-foreground mt-1 list-disc pl-5">
                  {f.errors.slice(0, 10).map((err, j) => (
                    <li key={j}>{err}</li>
                  ))}
                </ul>
              </details>
            ))}
        </div>
      ) : null}
    </SectionCard>
  );
}
