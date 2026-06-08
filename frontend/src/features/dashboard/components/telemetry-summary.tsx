import { Activity, Flame, Footprints, Gauge, HeartPulse, Moon, Wind } from "lucide-react";

import { EmptyState } from "@/components/async/empty-state";
import { MetricGrid } from "@/components/ui/metric-grid";
import { SectionCard } from "@/components/ui/section-card";
import { StatCard } from "@/components/ui/stat-card";
import type { TelemetrySummary as Telemetry } from "@/lib/gateway/types";

const round = (n: number) => Math.round(n).toLocaleString();
const hm = (min: number) => `${Math.floor(min / 60)}h ${Math.round(min % 60)}m`;

/**
 * Watch telemetry for the day. Complementary data: every field is optional, so a missing
 * signal shows a greyed "—" and an all-empty day shows "no watch data" — never an error.
 */
export function TelemetrySummary({ telemetry }: { telemetry: Telemetry }) {
  const { steps, energy_expenditure, avg_heart_rate, avg_stress, avg_spo2, sleep } = telemetry;
  const allEmpty =
    steps == null &&
    energy_expenditure == null &&
    avg_heart_rate == null &&
    avg_stress == null &&
    avg_spo2 == null &&
    !sleep?.total_min;

  return (
    <SectionCard title="Body" icon={<Activity className="size-4" />}>
      {allEmpty ? (
        <EmptyState
          title="No watch data"
          description="Telemetry syncs from your watch — this day has none. Manual logging is unaffected."
          className="border-0"
        />
      ) : (
        <div className="space-y-3">
          <MetricGrid>
            <StatCard
              label="Steps"
              value={steps}
              format={round}
              icon={<Footprints className="size-3.5" />}
            />
            <StatCard
              label="Energy"
              value={energy_expenditure}
              unit="kcal"
              format={round}
              icon={<Flame className="size-3.5" />}
            />
            <StatCard
              label="Avg HR"
              value={avg_heart_rate}
              unit="bpm"
              format={round}
              icon={<HeartPulse className="size-3.5" />}
            />
            <StatCard
              label="Stress"
              value={avg_stress}
              format={round}
              icon={<Gauge className="size-3.5" />}
            />
            <StatCard
              label="SpO₂"
              value={avg_spo2}
              unit="%"
              format={round}
              icon={<Wind className="size-3.5" />}
            />
            <StatCard
              label="Sleep"
              value={sleep?.total_min ?? null}
              format={hm}
              icon={<Moon className="size-3.5" />}
            />
          </MetricGrid>
          {sleep?.total_min ? (
            <p className="text-muted-foreground text-xs">
              {[
                sleep.deep_min != null && `Deep ${sleep.deep_min}m`,
                sleep.rem_min != null && `REM ${sleep.rem_min}m`,
                sleep.light_min != null && `Light ${sleep.light_min}m`,
                sleep.efficiency != null && `Efficiency ${sleep.efficiency}%`,
              ]
                .filter(Boolean)
                .join(" · ")}
            </p>
          ) : null}
        </div>
      )}
    </SectionCard>
  );
}
