import os
from typing import Any, Callable, Iterable, Optional, Sequence

from ..data_access.utils import establish_connection as _establish_connection

# Severity labels (can be overridden by environment variables if needed)
FATAL_LABEL = os.getenv("FATAL_LABEL", "Tue")
SEVERE_LABEL = os.getenv("SEVERE_LABEL", "Blessee hospitalisee")
LIGHT_LABEL = os.getenv("LIGHT_LABEL", "Blessee Leger")


def fetch_all(
    query: str,
    params: tuple = (),
    connect_func: Callable[[], Any] = _establish_connection,
) -> list[tuple[Any, ...]]:
    """Fetch rows for a SELECT query."""
    conn = connect_func()
    if not conn:
        raise RuntimeError("Database connection failed. Check DB_HOST / DB_PORT / credentials.")
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()


def print_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> None:
    """Print rows as a simple ASCII table."""
    if not rows:
        print("(no results)")
        return

    widths = [len(h) for h in headers]
    for r in rows:
        for i, v in enumerate(r):
            widths[i] = max(widths[i], len(str(v)))

    def fmt(vals: Sequence[Any]) -> str:
        return " | ".join(str(vals[i]).ljust(widths[i]) for i in range(len(headers)))

    print(fmt(headers))
    print("-+-".join("-" * w for w in widths))
    for r in rows:
        print(fmt(r))


def fetch_table_columns(schema: str, table: str) -> list[tuple[str, str]]:
    return fetch_all(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position;
        """,
        (schema, table),
    )


def compute_severity_breakdown() -> list[tuple[str, int]]:
    rows = fetch_all(
        """
        SELECT COALESCE(gravite_usager, 'UNKNOWN') AS gravite, COUNT(*)::int AS total
        FROM raw.accidents
        GROUP BY gravite
        ORDER BY total DESC;
        """
    )
    return [(str(g), int(t)) for g, t in rows]


def compute_fatal_rate() -> tuple[float, int, int]:
    rows = fetch_all(
        """
        SELECT
          ROUND(
            (SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(*), 0),
            3
          ) AS fatal_rate_percent,
          SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)::int AS fatalities,
          COUNT(*)::int AS total
        FROM raw.accidents;
        """,
        (FATAL_LABEL, FATAL_LABEL),
    )
    fatal_rate_percent, fatalities, total = rows[0]
    return float(fatal_rate_percent or 0.0), int(fatalities or 0), int(total or 0)


def list_collision_types() -> list[tuple[str, int]]:
    rows = fetch_all(
        """
        SELECT COALESCE(type_collision, 'UNKNOWN') AS type_collision, COUNT(*)::int AS total
        FROM raw.accidents
        GROUP BY type_collision
        ORDER BY total DESC;
        """
    )
    return [(str(tc), int(t)) for tc, t in rows]


def list_top_communes(limit: int = 10) -> list[tuple[str, int]]:
    rows = fetch_all(
        """
        SELECT COALESCE(commune, 'UNKNOWN') AS commune, COUNT(*)::int AS total
        FROM raw.accidents
        GROUP BY commune
        ORDER BY total DESC
        LIMIT %s;
        """,
        (limit,),
    )
    return [(str(c), int(t)) for c, t in rows]
