"use client";

import { Activity, Dumbbell, Flame } from "lucide-react";
import { toast } from "sonner";

import { EmptyState } from "@/components/async/empty-state";
import { ErrorCard } from "@/components/async/error-card";
import { Skeleton } from "@/components/async/skeleton";
import { GroupedBars } from "@/components/charts/grouped-bars";
import { TrendLine } from "@/components/charts/trend-line";
import { Field } from "@/components/form/field";
import { NumberInput } from "@/components/form/number-input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MetricGrid } from "@/components/ui/metric-grid";
import { SectionCard } from "@/components/ui/section-card";
import { Separator } from "@/components/ui/separator";
import { StatCard } from "@/components/ui/stat-card";

const WEIGHT = [
  { day: "2026-06-01", weight: 80.4, fat: 17.2 },
  { day: "2026-06-02", weight: 80.1, fat: 17.0 },
  { day: "2026-06-03", weight: 79.9, fat: 16.9 },
  { day: "2026-06-04", weight: 80.0, fat: 16.7 },
  { day: "2026-06-05", weight: 79.6, fat: 16.6 },
  { day: "2026-06-06", weight: 79.4, fat: 16.4 },
  { day: "2026-06-07", weight: 79.5, fat: 16.3 },
];

const SETS = [
  { muscle: "Chest", sets: 14 },
  { muscle: "Back", sets: 18 },
  { muscle: "Quads", sets: 8 },
  { muscle: "Shoulders", sets: 22 },
  { muscle: "Arms", sets: 12 },
];

function band(sets: number): string {
  if (sets < 10) return "var(--warning)";
  if (sets > 20) return "var(--destructive)";
  return "var(--success)";
}

function Row({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-3">
      <h2 className="text-muted-foreground text-sm font-semibold">{title}</h2>
      {children}
      <Separator className="mt-6" />
    </section>
  );
}

/** Dev-only gallery: every shared primitive with its variants and async states. */
export default function DesignSystemPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Design system</h1>
        <p className="text-muted-foreground text-sm">
          Shared primitives with their variants and loading / empty / error states.
        </p>
      </div>

      <Row title="Buttons">
        <div className="flex flex-wrap items-center gap-2">
          <Button>Default</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="destructive">Destructive</Button>
          <Button loading>Saving</Button>
          <Button size="sm">Small</Button>
          <Button size="icon" aria-label="Activity">
            <Activity />
          </Button>
        </div>
      </Row>

      <Row title="Badges">
        <div className="flex flex-wrap gap-2">
          <Badge>Default</Badge>
          <Badge variant="outline">Outline</Badge>
          <Badge variant="success">Recovered</Badge>
          <Badge variant="warning">Under target</Badge>
          <Badge variant="destructive">Over target</Badge>
          <Badge variant="info">Estimated</Badge>
        </div>
      </Row>

      <Row title="Stat cards (null → greyed —)">
        <MetricGrid>
          <StatCard label="Steps" value={10238} icon={<Activity className="size-3.5" />} />
          <StatCard label="Energy" value={2114} unit="kcal" icon={<Flame className="size-3.5" />} />
          <StatCard label="Body fat" value={16.3} unit="%" format={(n) => n.toFixed(1)} />
          <StatCard label="SpO₂" value={null} hint="from watch" />
        </MetricGrid>
      </Row>

      <Row title="Section card">
        <SectionCard
          title="Training"
          icon={<Dumbbell className="size-4" />}
          action={
            <Button size="sm" variant="outline">
              Add
            </Button>
          }
        >
          <p className="text-muted-foreground text-sm">Gym · 60 min · load 480</p>
        </SectionCard>
      </Row>

      <Row title="Form controls">
        <div className="grid max-w-md gap-4 sm:grid-cols-2">
          <Field id="d-name" label="Food">
            <Input id="d-name" placeholder="e.g. rice" />
          </Field>
          <Field id="d-weight" label="Weight" hint="working set">
            <NumberInput id="d-weight" unit="kg" placeholder="0" />
          </Field>
          <Field id="d-reps" label="Reps" error="Must be at least 1" required>
            <NumberInput id="d-reps" invalid defaultValue={0} />
          </Field>
        </div>
      </Row>

      <Row title="Charts (UTC in → local out)">
        <div className="grid gap-4 lg:grid-cols-2">
          <SectionCard title="Weight trend">
            <TrendLine
              data={WEIGHT}
              xKey="day"
              lines={[
                { key: "weight", label: "Weight (kg)" },
                { key: "fat", label: "Body fat (%)", color: "var(--warning)" },
              ]}
            />
          </SectionCard>
          <SectionCard title="Weekly sets / muscle">
            <GroupedBars
              data={SETS}
              xKey="muscle"
              bars={[{ key: "sets", label: "Sets" }]}
              targetBand={{ from: 10, to: 20 }}
              colorFor={(row) => band(row.sets)}
            />
          </SectionCard>
          <SectionCard title="Chart · loading">
            <TrendLine data={undefined} xKey="day" lines={[{ key: "weight" }]} loading />
          </SectionCard>
          <SectionCard title="Chart · empty">
            <TrendLine data={[]} xKey="day" lines={[{ key: "weight" }]} />
          </SectionCard>
        </div>
      </Row>

      <Row title="Async states">
        <div className="grid gap-4 sm:grid-cols-3">
          <Skeleton className="h-24 w-full" />
          <EmptyState description="No meals logged yet." />
          <ErrorCard message="Couldn't reach the server." onRetry={() => toast("Retried")} />
        </div>
      </Row>

      <Row title="Toasts">
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => toast.success("Meal logged")}>
            Success toast
          </Button>
          <Button variant="outline" onClick={() => toast.error("Couldn't save")}>
            Error toast
          </Button>
        </div>
      </Row>
    </div>
  );
}
