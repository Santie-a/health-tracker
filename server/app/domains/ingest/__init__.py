"""Ingest domain: import complementary telemetry from Samsung Health exports.

Spans multiple target tables (telemetry, sleep_sessions, body_composition,
training_sessions) so it lives at the top of domains rather than inside one. All
imports are additive and row-resilient — a bad row is skipped + logged, never
aborting the file (see ARCHITECTURE.md "Resilience").
"""
