"use client";

import { Camera, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { buttonVariants } from "@/components/ui/button";
import { ApiError } from "@/lib/query/fetcher";
import { useGatewayMutation } from "@/lib/query/use-gateway-mutation";
import { cn } from "@/lib/utils";

import { createPhotoMeal } from "../api";

/**
 * Meal-photo entry. Uploads to the gateway → image-svc. When that box is offline the
 * gateway returns a *degraded* empty meal (not an error); we still navigate to the meal
 * and flag `degraded` so the detail page shows the manual-entry banner.
 *
 * Mobile note: this is a real `<label>` wrapping the file input — NOT a button that
 * programmatically `.click()`s a hidden input. On Android, returning from the camera
 * activity can reload the page; a label-associated, user-tapped input delivers the
 * captured file far more reliably than a synthetic click into a `display:none` input
 * (whose handler/state may not survive the round-trip).
 */
export function PhotoUpload() {
  const router = useRouter();

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
    <label
      aria-busy={mutation.isPending}
      className={cn(
        buttonVariants({ variant: "outline", size: "sm" }),
        "cursor-pointer",
        mutation.isPending && "pointer-events-none opacity-50",
      )}
    >
      {mutation.isPending ? <Loader2 className="animate-spin" /> : <Camera />}
      Photo
      <input
        type="file"
        accept="image/*"
        capture="environment"
        disabled={mutation.isPending}
        className="sr-only"
        onChange={(e) => {
          const file = e.target.files?.[0];
          e.target.value = ""; // allow re-selecting the same file
          if (!file) return;
          if (file.size > 15_000_000) {
            toast.error("Image too large (max 15 MB).");
            return;
          }
          mutation.mutate(file, {
            onError: (err) =>
              toast.error(err instanceof ApiError ? err.friendly : "Upload failed"),
          });
        }}
      />
    </label>
  );
}
