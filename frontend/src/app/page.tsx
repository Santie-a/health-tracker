import { GatewayStatus } from "@/features/dashboard/components/gateway-status";

/**
 * Home / Today. Phase 0 placeholder: confirms the frontend ↔ gateway plumbing works
 * end-to-end. The real aggregated day view (GET /dashboard) lands in Phase 2.
 */
export default function HomePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Today</h1>
        <p className="text-muted-foreground text-sm">
          The dashboard lands in Phase 2. For now, here&apos;s the gateway connection.
        </p>
      </div>
      <GatewayStatus />
    </div>
  );
}
