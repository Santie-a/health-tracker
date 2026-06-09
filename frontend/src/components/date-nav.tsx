"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { formatISODate, shiftISODate, todayISODate } from "@/lib/time";

/**
 * Shared day selector: prev / next / today + a native date picker. Works in local
 * calendar dates (YYYY-MM-DD); "next" is capped at today since there's no future data.
 * Used by the Today dashboard and the nutrition day view.
 */
export function DateNav({ date, onChange }: { date: string; onChange: (date: string) => void }) {
  const today = todayISODate();
  const isToday = date >= today;

  return (
    <div className="flex items-center gap-2">
      <Button
        variant="outline"
        size="icon"
        aria-label="Previous day"
        onClick={() => onChange(shiftISODate(date, -1))}
      >
        <ChevronLeft />
      </Button>
      <input
        type="date"
        value={date}
        max={today}
        onChange={(e) => e.target.value && onChange(e.target.value)}
        className="bg-background focus-visible:ring-ring h-9 rounded-md border px-3 text-sm focus-visible:ring-2 focus-visible:outline-none"
      />
      <Button
        variant="outline"
        size="icon"
        aria-label="Next day"
        disabled={isToday}
        onClick={() => onChange(shiftISODate(date, 1))}
      >
        <ChevronRight />
      </Button>
      {!isToday ? (
        <Button variant="ghost" size="sm" onClick={() => onChange(today)}>
          Today
        </Button>
      ) : (
        <span className="text-muted-foreground text-sm">{formatISODate(date)}</span>
      )}
    </div>
  );
}
