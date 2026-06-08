import { format, parseISO } from "date-fns";

/**
 * The single home for time conversion. Rule: the gateway speaks UTC, the UI shows
 * local. Components import these helpers and never touch `new Date(string)` directly
 * — that path silently misreads the gateway's *naive* UTC timestamps as local time.
 *
 * - Calendar dates (`YYYY-MM-DD`) are used for day-scoped queries (dashboard, meals,
 *   recommendations). They're computed in the user's local zone.
 * - Instants (full datetimes) come back from the gateway as ISO strings, sometimes
 *   without a `Z`. `parseInstant` treats a missing zone as UTC, then formatting renders
 *   in local time.
 */

/** Today's calendar date in the user's local zone, as `YYYY-MM-DD`. */
export function todayISODate(): string {
  return format(new Date(), "yyyy-MM-dd");
}

/** Add/subtract days from a `YYYY-MM-DD` string, returning `YYYY-MM-DD`. */
export function shiftISODate(isoDate: string, days: number): string {
  const d = parseISO(isoDate);
  d.setDate(d.getDate() + days);
  return format(d, "yyyy-MM-dd");
}

/**
 * Parse a gateway instant into a Date. A trailing `Z` or explicit offset is honored;
 * a *naive* string (no zone) is interpreted as UTC, matching the gateway's contract
 * ("naive assumed UTC").
 */
export function parseInstant(iso: string): Date {
  return new Date(hasZone(iso) ? iso : `${iso}Z`);
}

function hasZone(iso: string): boolean {
  return /[zZ]$|[+-]\d{2}:?\d{2}$/.test(iso);
}

/** Format a gateway instant in the user's local zone (default: "MMM d, h:mm a"). */
export function formatInstant(iso: string, pattern = "MMM d, h:mm a"): string {
  return format(parseInstant(iso), pattern);
}

/** Format a `YYYY-MM-DD` calendar date for display (default: "EEE, MMM d"). */
export function formatISODate(isoDate: string, pattern = "EEE, MMM d"): string {
  return format(parseISO(isoDate), pattern);
}

/** A `Date` (or now) as a UTC ISO instant — for posting `ts` fields to the gateway. */
export function toInstantISO(date: Date = new Date()): string {
  return date.toISOString();
}
