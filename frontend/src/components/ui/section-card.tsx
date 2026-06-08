import type { ReactNode } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "./card";

/**
 * A titled dashboard section with an optional header action (e.g. "Add", "View all").
 * The standard container each Today/Trends widget renders into.
 */
export function SectionCard({
  title,
  icon,
  action,
  children,
  className,
}: {
  title: string;
  icon?: ReactNode;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <Card className={className}>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle className="flex items-center gap-2 text-base">
          {icon}
          {title}
        </CardTitle>
        {action}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}
