import re
from typing import Any, Iterable, Optional, Sequence

from ..data_access.utils import establish_connection

# (optional) menu: does not affect tests if not used
try:
    from .accident_cli import run_menu
except Exception:  # pragma: no cover
    run_menu = None


# Severity labels
FATAL_LABEL = "Tue"
SEVERE_LABEL = "Blessee hospitalisee"
LIGHT_LABEL = "Blessee Leger"

HELP_TEXT = """
Road Safety interactive CLI

General:
  help
  exit
  menu                          -> open menu (optional)

Overview / severity:
  overview                       -> severity breakdown + total
  fatal_rate                     -> fatal proportion
  collisions                     -> most frequent collision types
  gravity_values 20             -> show distinct gravite_usager values

Time:
  by_hour                        -> accidents per hour
  day_vs_night                   -> stats grouped by luminosite
  by_month                       -> accidents per month
  weekend_vs_week                -> compare weekend vs week (counts + fatal/severe)

Location:
  top_communes 10                -> top communes by total accidents
  stats commune Paris            -> KPIs for a commune (total, fatal, severe)

Extended:
  top_fatal_communes 10
  top_severe_communes 10
  risk_score_communes 10
  risk_score commune Paris
  trend_days 2026-01-01 2026-01-31
  trend_days 2026-01-01 2026-01-31 commune Paris

Introspection:
  columns raw accidents
"""


# ---------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------

def fetch_all(query: str, params: tuple = ()) -> list[tuple[Any, ...]]:
    """Fetch rows for a SELECT query."""
    conn = establish_connection()
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


def print_kv(title: str, rows: Iterable[tuple[Any, Any]]) -> None:
    """Print key/value rows."""
    print(title)
    for k, v in rows:
        print(f"- {k}: {v}")


# ---------------------------------------------------------------------
# Introspection
# ---------------------------------------------------------------------

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


# ---------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------

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


def list_gravity_values(limit: int = 50) -> list[tuple[str, int]]:
    rows = fetch_all(
        """
        SELECT COALESCE(gravite_usager, 'NULL') AS gravite, COUNT(*)::int AS total
        FROM raw.accidents
        GROUP BY gravite
        ORDER BY total DESC
        LIMIT %s;
        """,
        (limit,),
    )
    return [(str(g), int(t)) for g, t in rows]


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


def compute_commune_kpis(commune: str) -> tuple[int, int, int]:
    rows = fetch_all(
        """
        SELECT
          COUNT(*)::int AS total,
          SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)::int AS fatalities,
          SUM(CASE WHEN gravite_usager IN (%s, %s) THEN 1 ELSE 0 END)::int AS severe
        FROM raw.accidents
        WHERE LOWER(commune) = LOWER(%s);
        """,
        (FATAL_LABEL, FATAL_LABEL, SEVERE_LABEL, commune),
    )
    total, fatalities, severe = rows[0]
    return int(total or 0), int(fatalities or 0), int(severe or 0)


def compute_risk_score_by_commune(limit: int = 10) -> list[tuple[str, int, int, int, int]]:
    rows = fetch_all(
        """
        SELECT
          COALESCE(commune, 'UNKNOWN') AS commune,
          SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)::int AS fatalities,
          SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)::int AS severe,
          SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)::int AS light,
          (
            3 * SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)
            + 2 * SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)
            + 1 * SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)
          )::int AS risk_score
        FROM raw.accidents
        GROUP BY commune
        ORDER BY risk_score DESC
        LIMIT %s;
        """,
        (FATAL_LABEL, SEVERE_LABEL, LIGHT_LABEL, FATAL_LABEL, SEVERE_LABEL, LIGHT_LABEL, limit),
    )
    return [(str(c), int(f), int(s), int(l), int(rs)) for c, f, s, l, rs in rows]


def compute_commune_risk_score(commune: str) -> tuple[int, int, int, int]:
    rows = fetch_all(
        """
        SELECT
          SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)::int AS fatalities,
          SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)::int AS severe,
          SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)::int AS light,
          (
            3 * SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)
            + 2 * SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)
            + 1 * SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)
          )::int AS risk_score
        FROM raw.accidents
        WHERE LOWER(commune) = LOWER(%s);
        """,
        (FATAL_LABEL, SEVERE_LABEL, LIGHT_LABEL, FATAL_LABEL, SEVERE_LABEL, LIGHT_LABEL, commune),
    )
    f, s, l, rs = rows[0]
    return int(f or 0), int(s or 0), int(l or 0), int(rs or 0)


def compute_trend_days(date_from: str, date_to: str, commune: Optional[str] = None) -> list[tuple[str, int]]:
    if commune:
        rows = fetch_all(
            """
            SELECT date_acc::date::text AS day, COUNT(*)::int AS total
            FROM raw.accidents
            WHERE date_acc BETWEEN %s AND %s
              AND LOWER(commune) = LOWER(%s)
            GROUP BY day
            ORDER BY day;
            """,
            (date_from, date_to, commune),
        )
    else:
        rows = fetch_all(
            """
            SELECT date_acc::date::text AS day, COUNT(*)::int AS total
            FROM raw.accidents
            WHERE date_acc BETWEEN %s AND %s
            GROUP BY day
            ORDER BY day;
            """,
            (date_from, date_to),
        )
    return [(str(d), int(t)) for d, t in rows]


# ---------------------------------------------------------------------
# Command wrappers (q_*)
# ---------------------------------------------------------------------

def q_overview() -> None:
    print_table(["gravite_usager", "total"], compute_severity_breakdown())


def q_fatal_rate() -> None:
    rate, fatalities, total = compute_fatal_rate()
    print_table(["fatal_rate_%", "fatalities", "total"], [(rate, fatalities, total)])


def q_collisions() -> None:
    rows = list_collision_types()
    print_table(["type_collision", "total"], rows)


def q_gravity_values(limit: int) -> None:
    rows = list_gravity_values(limit)
    print_table(["gravite_usager", "total"], rows)


def q_top_communes(limit: int) -> None:
    rows = list_top_communes(limit)
    print_table(["commune", "total"], rows)


def q_stats_commune(commune: str) -> None:
    total, fatalities, severe = compute_commune_kpis(commune)
    print_table(["commune", "total", "fatalities", "severe"], [(commune, total, fatalities, severe)])


def q_risk_score_communes(limit: int) -> None:
    rows = compute_risk_score_by_commune(limit)
    print_table(["commune", "fatalities", "severe", "light", "risk_score"], rows)


def q_risk_score_commune(commune: str) -> None:
    f, s, l, rs = compute_commune_risk_score(commune)
    print_table(["commune", "fatalities", "severe", "light", "risk_score"], [(commune, f, s, l, rs)])


def q_trend_days(date_from: str, date_to: str, commune: Optional[str]) -> None:
    rows = compute_trend_days(date_from, date_to, commune)
    print_table(["day", "total"], rows)


def q_columns(schema: str, table: str) -> None:
    rows = fetch_table_columns(schema, table)
    print_table(["column_name", "data_type"], rows)


# ---------------------------------------------------------------------
# REPL (tests expect this behaviour)
# ---------------------------------------------------------------------

def run_chat() -> None:
    print("=== Road Safety Interactive ===")
    print("Type 'help' for commands, 'exit' to quit.")

    while True:
        q = input("\n> ").strip()
        if not q:
            continue

        low = q.lower()

        if low in {"exit", "quit"}:
            print("Bye.")
            return

        if low in {"help", "h", "?"}:
            print(HELP_TEXT)
            continue

        if low == "menu" and run_menu is not None:
            run_menu()
            continue

        if low == "overview":
            q_overview()
            continue

        if low == "fatal_rate":
            q_fatal_rate()
            continue

        # Parameterized commands used by tests
        m = re.match(r"^top_communes\s+(\d+)$", q, re.IGNORECASE)
        if m:
            q_top_communes(int(m.group(1)))
            continue

        m = re.match(r"^stats\s+commune\s+(.+)$", q, re.IGNORECASE)
        if m:
            q_stats_commune(m.group(1).strip())
            continue

        m = re.match(r"^risk_score\s+commune\s+(.+)$", q, re.IGNORECASE)
        if m:
            q_risk_score_commune(m.group(1).strip())
            continue

        m = re.match(
            r"^trend_days\s+(\d{4}-\d{2}-\d{2})\s+(\d{4}-\d{2}-\d{2})(?:\s+commune\s+(.+))?$",
            q,
            re.IGNORECASE,
        )
        if m:
            date_from = m.group(1)
            date_to = m.group(2)
            commune = m.group(3).strip() if m.group(3) else None
            q_trend_days(date_from, date_to, commune)
            continue

        m = re.match(r"^columns\s+([a-zA-Z_][\w]*)\s+([a-zA-Z_][\w]*)$", q, re.IGNORECASE)
        if m:
            q_columns(m.group(1), m.group(2))
            continue

        print("Unknown command. Type 'help' to see available commands.")
