import { EmptyState } from "@/components/async/empty-state";

/** Stand-in for a view not yet built, so nav links resolve during the phased build. */
export function Placeholder({ title, phase }: { title: string; phase: string }) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
      <EmptyState title="Coming soon" description={`This view lands in ${phase}.`} />
    </div>
  );
}
