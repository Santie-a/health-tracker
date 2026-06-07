# Database migrations (Alembic)

The **base** relational schema lives in `db/initdb/*.sql` (it also sets up the
Timescale hypertable, continuous aggregate, and retention policy — things Alembic
does not manage). Alembic owns only the **deltas** on top of that base.

To avoid duplicating DDL in two places, baseline revision `0001` is an empty
marker representing "the initdb schema is present". The migration chain is:

```
0001  baseline (initdb base — empty marker)
0002  strength catalog + serving-based nutrition (new tables + columns)
0003  swim/cardio session metrics (training_sessions columns)
```

The DB URL is read from `DATABASE_URL` (app Settings / `.env`) — it is **not**
stored in `alembic.ini`.

## Bringing up a database

**Existing DB created by `db/initdb` (the normal case — dev container & Pi5):**
```bash
alembic stamp 0001      # mark the base as present WITHOUT re-creating it
alembic upgrade head    # apply 0002, 0003, ...
```

**On every deploy afterward** (DEPLOY.md "run DB migrations on deploy"):
```bash
alembic upgrade head
```

> A pure Alembic-only bring-up (no `initdb`) is not supported by design — the base
> DDL has a single source of truth. The project standardizes on the db container.

## Adding a migration

Hand-write it (do **not** trust autogenerate — it doesn't understand the
hypertable/continuous-aggregate and will emit destructive diffs):

```bash
alembic revision -m "what changed"      # creates a stub in versions/
# edit the stub: explicit revision id, upgrade(), downgrade()
alembic upgrade head --sql              # review the SQL offline first
alembic upgrade head                    # apply
```

Once a set of changes is stable, fold the same tables/columns into `db/initdb`
so a fresh bring-up matches (per db/TODO.md), keeping `0001` the baseline.
