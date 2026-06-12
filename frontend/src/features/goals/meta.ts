import type { BadgeProps } from "@/components/ui/badge";
import type { GoalMetric, GoalProgressStatus, GoalType } from "@/lib/gateway/types";

/** Human label per goal type. */
export const GOAL_TYPE_LABEL: Record<GoalType, string> = {
  gain_muscle: "Lean bulk",
  gain_weight: "Gain weight",
  lose_fat: "Lose fat",
  recomp: "Recomp",
  maintain: "Maintain",
  improve_sleep: "Improve sleep",
};

/** One-line description shown in the create picker. */
export const GOAL_TYPE_HINT: Record<GoalType, string> = {
  gain_muscle: "Controlled surplus, high protein — add muscle while limiting fat.",
  gain_weight: "Scale weight trending up at a steady rate.",
  lose_fat: "Calorie deficit with protein held high to keep muscle.",
  recomp: "Hold weight, shift composition toward muscle.",
  maintain: "Stay at your current weight.",
  improve_sleep: "Hit a nightly sleep target consistently.",
};

const METRIC_META: Record<GoalMetric, { unit: string; decimals: number; asHours?: boolean }> = {
  weight_kg: { unit: "kg", decimals: 1 },
  skeletal_muscle_kg: { unit: "kg", decimals: 1 },
  body_fat_pct: { unit: "%", decimals: 1 },
  sleep_min: { unit: "h", decimals: 1, asHours: true },
  sleep_efficiency: { unit: "%", decimals: 0 },
};

export function metricLabel(metric: GoalMetric | null | undefined): string {
  switch (metric) {
    case "weight_kg":
      return "Weight";
    case "skeletal_muscle_kg":
      return "Muscle";
    case "body_fat_pct":
      return "Body fat";
    case "sleep_min":
      return "Sleep";
    case "sleep_efficiency":
      return "Sleep efficiency";
    default:
      return "Metric";
  }
}

/** Format a metric value with its unit (sleep minutes render as hours). */
export function formatMetric(
  value: number | null | undefined,
  metric: GoalMetric | null | undefined,
): string {
  if (value == null) return "—";
  const m = (metric && METRIC_META[metric]) || { unit: "", decimals: 1, asHours: false };
  const n = m.asHours ? value / 60 : value;
  return `${n.toFixed(m.decimals)} ${m.unit}`.trim();
}

/** Format a weekly rate with a sign (e.g. "+0.25 kg/wk", "−0.45 kg/wk"). */
export function formatRate(
  rate: number | null | undefined,
  metric: GoalMetric | null | undefined,
): string {
  if (rate == null) return "—";
  const m = (metric && METRIC_META[metric]) || { unit: "", decimals: 2, asHours: false };
  const n = m.asHours ? rate / 60 : rate;
  const sign = n > 0 ? "+" : n < 0 ? "−" : "";
  return `${sign}${Math.abs(n).toFixed(2)} ${m.unit}/wk`.trim();
}

/** Progress status → badge variant + label. */
export const PROGRESS_META: Record<
  GoalProgressStatus,
  { label: string; variant: BadgeProps["variant"] }
> = {
  on_track: { label: "On track", variant: "success" },
  ahead: { label: "Ahead", variant: "info" },
  behind: { label: "Behind", variant: "warning" },
  too_fast: { label: "Too fast", variant: "warning" },
  stalled: { label: "Stalled", variant: "warning" },
  achieved: { label: "Achieved", variant: "success" },
  no_target: { label: "No target", variant: "info" },
  no_data: { label: "No data", variant: "default" },
};

/** Ring/accent color (CSS var) per progress status. */
export function progressColor(status: GoalProgressStatus): string {
  switch (status) {
    case "on_track":
    case "achieved":
      return "var(--success)";
    case "behind":
    case "stalled":
    case "too_fast":
      return "var(--warning)";
    default:
      return "var(--primary)";
  }
}
