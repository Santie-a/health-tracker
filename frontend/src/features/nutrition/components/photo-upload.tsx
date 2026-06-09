"use client";

import { Camera } from "lucide-react";
import { useRouter } from "next/navigation";
import { useRef } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/query/fetcher";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";

import { createPhotoMeal } from "../api";

/**
 * Meal-photo entry. Uploads to the gateway → image-svc. When that box is offline the
 * gateway returns a *degraded* empty meal (not an error); we still navigate to the meal
 * and flag `degraded` so the detail page shows the manual-entry banner.
 */
export function PhotoUpload() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);

  const mutation = useGatewayMutation({
    mutationFn: (file: File) => {
      const form = new FormData();
      form.append("image", file);
      return createPhotoMeal(form);
    },
    invalidate: [["nutrition"], ["dashboard"]],
    onSuccess: (res) => {
      if (res.degraded) {
        toast.warning(res.note ?? "Photo service offline — add items manually.");
      } else {
        toast.success("Photo analyzed");
      }
      router.push(`/nutrition/${res.meal.id}?degraded=${res.degraded ? 1 : 0}`);
    },
  });

  return (
    <>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          e.target.value = ""; // allow re-selecting the same file
          if (!file) return;
          if (file.size > 15_000_000) {
            toast.error("Image too large (max 15 MB).");
            return;
          }
          mutation.mutate(file, {
            onError: (err) => toast.error(err instanceof ApiError ? err.friendly : "Upload failed"),
          });
        }}
      />
      <Button
        variant="outline"
        size="sm"
        loading={mutation.isPending}
        onClick={() => inputRef.current?.click()}
      >
        <Camera /> Photo
      </Button>
    </>
  );
}
