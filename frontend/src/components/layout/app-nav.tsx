"use client";

import {
  Activity,
  CalendarDays,
  Dumbbell,
  LineChart,
  Sparkles,
  Target,
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
  { href: "/goals", label: "Goals", icon: Target },
  { href: "/recommendations", label: "Advice", icon: Sparkles },
  { href: "/import", label: "Import", icon: Upload },
] as const;

function isActive(pathname: string, href: string): boolean {
  return href === "/" ? pathname === "/" : pathname.startsWith(href);
}

function Brand() {
  return (
    <Link href="/" className="flex items-center gap-2 font-semibold">
      <Activity className="text-primary size-5" />
      Health Tracker
    </Link>
  );
}

/**
 * App chrome. Desktop: a top bar with brand + nav + theme toggle. Phone: a slim top bar
 * (brand + theme toggle) plus a fixed bottom bar for thumb-reachable navigation.
 */
export function AppNav() {
  const pathname = usePathname();

  return (
    <>
      {/* Desktop / tablet: top bar */}
      <header className="bg-background/80 sticky top-0 z-40 hidden border-b backdrop-blur sm:block">
        <div className="mx-auto flex h-14 max-w-5xl items-center gap-1 px-4">
          <div className="mr-3">
            <Brand />
          </div>
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

      {/* Phone: slim top bar (brand + theme toggle) */}
      <header className="bg-background/80 sticky top-0 z-40 flex h-12 items-center justify-between border-b px-4 backdrop-blur sm:hidden">
        <Brand />
        <ThemeToggle />
      </header>

      {/* Phone: fixed bottom bar */}
      <nav className="bg-background/95 fixed inset-x-0 bottom-0 z-40 grid grid-cols-7 border-t backdrop-blur sm:hidden">
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
