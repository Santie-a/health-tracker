"""Dashboard domain: one aggregated day view powering the frontend home.

Pure aggregator — composes the other domains' services into a single payload so
the frontend makes one call per day instead of five.
"""
