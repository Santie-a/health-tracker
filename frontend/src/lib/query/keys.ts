/**
 * Central query-key factory. One source of truth for cache keys so invalidation is
 * consistent across features (e.g. logging a meal invalidates both the day's nutrition
 * and the dashboard). Keys are readonly tuples — `as const` keeps them literal-typed.
 */

export const queryKeys = {
  health: ["health"] as const,

  dashboard: (date: string) => ["dashboard", date] as const,

  training: {
    list: (filters?: Record<string, unknown>) => ["training", "list", filters ?? {}] as const,
    session: (id: number) => ["training", "session", id] as const,
    stats: (from?: string, to?: string) => ["training", "stats", { from, to }] as const,
  },

  exercises: (query?: Record<string, unknown>) => ["exercises", query ?? {}] as const,

  nutrition: {
    day: (date: string) => ["nutrition", "day", date] as const,
    meal: (id: number) => ["nutrition", "meal", id] as const,
  },

  foods: {
    search: (q?: string) => ["foods", "search", q ?? ""] as const,
    recent: ["foods", "recent"] as const,
  },

  telemetry: {
    daily: (metric: string, from?: string, to?: string) =>
      ["telemetry", "daily", metric, { from, to }] as const,
    sleep: (from?: string, to?: string) => ["telemetry", "sleep", { from, to }] as const,
    bodyComposition: (from?: string, to?: string) => ["telemetry", "body", { from, to }] as const,
  },

  recommendations: (date: string) => ["recommendations", date] as const,

  goals: {
    list: (status?: string) => ["goals", "list", status ?? "all"] as const,
    active: ["goals", "active"] as const,
  },
} as const;
