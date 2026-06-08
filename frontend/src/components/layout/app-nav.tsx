"use client";

import {
  Activity,
  CalendarDays,
  Dumbbell,
  LineChart,
  Sparkles,
  Upload,
  UtensilsCrossed,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { ThemeToggle } from "@/components/theme/theme-toggle";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Today", icon: CalendarDays },
  { href: "/training", label: "Training", icon: Dumbbell },
  { href: "/nutrition", label: "Nutrition", icon: UtensilsCrossed },
  { href: "/trends", label: "Trends", icon: LineChart },
  { href: "/recommendations", label: "Advice", icon: Sparkles },
  { href: "/import", label: "Import", icon: Upload },
] as const;

function isActive(pathname: string, href: string): boolean {
  return href === "/" ? pathname === "/" : pathname.startsWith(href);
}

/**
 * App chrome: brand + primary nav + theme toggle. Renders as a top bar on desktop and
 * a fixed bottom bar on phones (thumb-reachable) — logging happens from mobile.
 */
export function AppNav() {
  const pathname = usePathname();

  return (
    <>
      {/* Desktop / tablet: top bar */}
      <header className="bg-background/80 sticky top-0 z-40 hidden border-b backdrop-blur sm:block">
        <div className="mx-auto flex h-14 max-w-5xl items-center gap-1 px-4">
          <Link href="/" className="mr-3 flex items-center gap-2 font-semibold">
            <Activity className="text-primary size-5" />
            Health Tracker
          </Link>
          <nav className="flex items-center gap-1">
            {NAV.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className={cn(
                  "inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                  isActive(pathname, href)
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                <Icon className="size-4" />
                {label}
              </Link>
            ))}
          </nav>
          <div className="ml-auto">
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Phone: fixed bottom bar */}
      <nav className="bg-background/95 fixed inset-x-0 bottom-0 z-40 grid grid-cols-6 border-t backdrop-blur sm:hidden">
        {NAV.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex flex-col items-center gap-0.5 py-2 text-[11px] font-medium transition-colors",
              isActive(pathname, href) ? "text-primary" : "text-muted-foreground",
            )}
          >
            <Icon className="size-5" />
            {label}
          </Link>
        ))}
      </nav>
    </>
  );
}
