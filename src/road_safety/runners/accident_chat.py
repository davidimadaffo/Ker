import re
from typing import Any, Iterable, Optional, Sequence

from ..data_access.utils import establish_connection


# Severity labels
FATAL_LABEL = "Tue"
SEVERE_LABEL = "Blessee hospitalisee"
LIGHT_LABEL = "Blessee Leger"

HELP_TEXT = """
Road Safety interactive CLI (prompt-only)

General:
  help
  exit

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

Users / vehicles:
  severe_by_age                  -> severe accidents by age group
  two_wheels_severe              -> severe rate for accidents involving moto
  pedestrian_rate                -> pedestrians/users ratio
  weather_impact                 -> grouped by cond_atmos

Extended (requested):
  top_fatal_communes 10          -> top communes by fatal accidents (Tué)
  top_severe_communes 10         -> top communes by severe accidents (Tué + Blessé hospitalisé)
  risk_score_communes 10         -> weighted risk score by commune
  risk_score commune Paris       -> weighted risk score for a single commune
  trend_days 2026-01-01 2026-01-31
  trend_days 2026-01-01 2026-01-31 commune Paris

Introspection:
  columns raw accidents          -> fetch_table_columns(schema, table)

Notes:
- Some queries depend on your exact labels (e.g. gravite_usager values like 'Tué').
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
    """
    Introspect column names + data types for a given schema/table.
    Returns rows: (column_name, data_type)
    """
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
# Analytics (action verbs: compute_*, list_*)
# ---------------------------------------------------------------------

def compute_severity_breakdown() -> list[tuple[str, int]]:
    """Group by gravite_usager."""
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
    """Compute fatal proportion (Tue / total) in percent."""
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
    """List collision types by frequency."""
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
    """List distinct gravite_usager values and counts."""
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

def compute_hourly_distribution() -> list[tuple[int, int]]:
    """Accidents per hour."""
    rows = fetch_all(
        """
        SELECT EXTRACT(HOUR FROM heure_acc)::int AS hour, COUNT(*)::int AS total
        FROM raw.accidents
        WHERE heure_acc IS NOT NULL
        GROUP BY hour
        ORDER BY total DESC;
        """
    )
    return [(int(h), int(t)) for h, t in rows]


def compute_day_vs_night_stats() -> list[tuple[str, int, int, int]]:
    """Group by luminosite: total, fatalities, severe."""
    rows = fetch_all(
        """
        SELECT COALESCE(luminosite, 'UNKNOWN') AS luminosite,
               COUNT(*)::int AS total,
               SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)::int AS fatalities,
               SUM(CASE WHEN gravite_usager IN (%s, %s) THEN 1 ELSE 0 END)::int AS severe
        FROM raw.accidents
        GROUP BY luminosite
        ORDER BY total DESC;
        """,
        (FATAL_LABEL, FATAL_LABEL, SEVERE_LABEL),
    )
    return [(str(l), int(t), int(f), int(s)) for l, t, f, s in rows]


def compute_monthly_distribution() -> list[tuple[int, int]]:
    """Accidents per month."""
    rows = fetch_all(
        """
        SELECT EXTRACT(MONTH FROM date_acc)::int AS month, COUNT(*)::int AS total
        FROM raw.accidents
        WHERE date_acc IS NOT NULL
        GROUP BY month
        ORDER BY total DESC;
        """
    )
    return [(int(m), int(t)) for m, t in rows]


def compute_weekend_severity_gap() -> list[tuple[str, int, int, int]]:
    """Compare weekend vs week: total, fatalities, severe."""
    rows = fetch_all(
        """
        SELECT
          CASE WHEN EXTRACT(ISODOW FROM date_acc) IN (6, 7) THEN 'weekend' ELSE 'week' END AS period,
          COUNT(*)::int AS total,
          SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)::int AS fatalities,
          SUM(CASE WHEN gravite_usager IN (%s, %s) THEN 1 ELSE 0 END)::int AS severe
        FROM raw.accidents
        WHERE date_acc IS NOT NULL
        GROUP BY period
        ORDER BY total DESC;
        """,
        (FATAL_LABEL, FATAL_LABEL, SEVERE_LABEL),
    )
    return [(str(p), int(t), int(f), int(s)) for p, t, f, s in rows]


def list_top_communes(limit: int = 10) -> list[tuple[str, int]]:
    """Top communes by total accidents."""
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


def compute_severe_by_age_group() -> list[tuple[str, int]]:
    rows = fetch_all(
        """
        SELECT
          CASE
            WHEN age_usager IS NULL THEN 'UNKNOWN'
            WHEN age_usager < 18 THEN '<18'
            WHEN age_usager BETWEEN 18 AND 24 THEN '18-24'
            WHEN age_usager BETWEEN 25 AND 34 THEN '25-34'
            WHEN age_usager BETWEEN 35 AND 44 THEN '35-44'
            WHEN age_usager BETWEEN 45 AND 54 THEN '45-54'
            WHEN age_usager BETWEEN 55 AND 64 THEN '55-64'
            WHEN age_usager BETWEEN 65 AND 74 THEN '65-74'
            ELSE '75+'
          END AS age_group,
          COUNT(*)::int AS severe_accidents
        FROM raw.accidents
        WHERE gravite_usager IN (%s, %s)
        GROUP BY age_group
        ORDER BY severe_accidents DESC;
        """,
        (FATAL_LABEL, SEVERE_LABEL),
    )
    return [(str(g), int(t)) for g, t in rows]


def compute_two_wheels_severe_rate() -> tuple[float, int]:
    """Severe rate for accidents involving moto (heuristic via ILIKE '%moto%')."""
    rows = fetch_all(
        """
        SELECT
          ROUND(
            (SUM(CASE WHEN gravite_usager IN (%s, %s) THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(*), 0),
            3
          ) AS severe_rate_percent,
          COUNT(*)::int AS total
        FROM raw.accidents
        WHERE (type_vehicule_1 ILIKE '%moto%' OR type_vehicule_2 ILIKE '%moto%');
        """,
        (FATAL_LABEL, SEVERE_LABEL),
    )
    severe_rate, total = rows[0]
    return float(severe_rate or 0.0), int(total or 0)


def compute_pedestrian_rate() -> tuple[float, int, int]:
    """Pedestrians/users ratio in percent based on sums of nombre_pietons / nombre_usagers."""
    rows = fetch_all(
        """
        SELECT
          ROUND(
            (SUM(COALESCE(nombre_pietons, 0)) * 100.0) / NULLIF(SUM(COALESCE(nombre_usagers, 0)), 0),
            3
          ) AS ped_rate_percent,
          SUM(COALESCE(nombre_pietons, 0))::int AS pedestrians,
          SUM(COALESCE(nombre_usagers, 0))::int AS users
        FROM raw.accidents;
        """
    )
    rate, pedestrians, users = rows[0]
    return float(rate or 0.0), int(pedestrians or 0), int(users or 0)


def compute_weather_impact() -> list[tuple[str, int, int, int]]:
    """Grouped by cond_atmos: total, fatalities, severe."""
    rows = fetch_all(
        """
        SELECT COALESCE(cond_atmos, 'UNKNOWN') AS cond_atmos,
               COUNT(*)::int AS total,
               SUM(CASE WHEN gravite_usager = %s THEN 1 ELSE 0 END)::int AS fatalities,
               SUM(CASE WHEN gravite_usager IN (%s, %s) THEN 1 ELSE 0 END)::int AS severe
        FROM raw.accidents
        GROUP BY cond_atmos
        ORDER BY total DESC;
        """,
        (FATAL_LABEL, FATAL_LABEL, SEVERE_LABEL),
    )
    return [(str(c), int(t), int(f), int(s)) for c, t, f, s in rows]


def list_top_fatal_communes(limit: int = 10) -> list[tuple[str, int]]:
    rows = fetch_all(
        """
        SELECT COALESCE(commune, 'UNKNOWN') AS commune, COUNT(*)::int AS fatalities
        FROM raw.accidents
        WHERE gravite_usager = %s
        GROUP BY commune
        ORDER BY fatalities DESC
        LIMIT %s;
        """,
        (FATAL_LABEL, limit),
    )
    return [(str(c), int(t)) for c, t in rows]


def list_top_severe_communes(limit: int = 10) -> list[tuple[str, int]]:
    rows = fetch_all(
        """
        SELECT COALESCE(commune, 'UNKNOWN') AS commune, COUNT(*)::int AS severe_accidents
        FROM raw.accidents
        WHERE gravite_usager IN (%s, %s)
        GROUP BY commune
        ORDER BY severe_accidents DESC
        LIMIT %s;
        """,
        (FATAL_LABEL, SEVERE_LABEL, limit),
    )
    return [(str(c), int(t)) for c, t in rows]


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
    """Daily trend between two dates (inclusive)."""
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
# Command wrappers (q_* = print-friendly)
# ---------------------------------------------------------------------

def q_overview() -> None:
    rows = compute_severity_breakdown()
    print_table(["gravite_usager", "total"], rows)


def q_fatal_rate() -> None:
    rate, fatalities, total = compute_fatal_rate()
    print_table(["fatal_rate_%", "fatalities", "total"], [(rate, fatalities, total)])


def q_collisions() -> None:
    rows = list_collision_types()
    print_table(["type_collision", "total"], rows)


def q_gravity_values(limit: int) -> None:
    rows = list_gravity_values(limit)
    print_table(["gravite_usager", "total"], rows)


def q_by_hour() -> None:
    rows = compute_hourly_distribution()
    print_table(["hour", "total"], rows)


def q_day_vs_night() -> None:
    rows = compute_day_vs_night_stats()
    print_table(["luminosite", "total", "fatalities", "severe"], rows)


def q_by_month() -> None:
    rows = compute_monthly_distribution()
    print_table(["month", "total"], rows)


def q_weekend_vs_week() -> None:
    rows = compute_weekend_severity_gap()
    print_table(["period", "total", "fatalities", "severe"], rows)


def q_top_communes(limit: int) -> None:
    rows = list_top_communes(limit)
    print_table(["commune", "total"], rows)


def q_stats_commune(commune: str) -> None:
    total, fatalities, severe = compute_commune_kpis(commune)
    print_table(["commune", "total", "fatalities", "severe"], [(commune, total, fatalities, severe)])


def q_severe_by_age() -> None:
    rows = compute_severe_by_age_group()
    print_table(["age_group", "severe_accidents"], rows)


def q_two_wheels_severe() -> None:
    rate, total = compute_two_wheels_severe_rate()
    print_table(["severe_rate_%", "total"], [(rate, total)])


def q_pedestrian_rate() -> None:
    rate, pedestrians, users = compute_pedestrian_rate()
    print_table(["ped_rate_%", "pedestrians", "users"], [(rate, pedestrians, users)])


def q_weather_impact() -> None:
    rows = compute_weather_impact()
    print_table(["cond_atmos", "total", "fatalities", "severe"], rows)


def q_top_fatal_communes(limit: int) -> None:
    rows = list_top_fatal_communes(limit)
    print_table(["commune", "fatalities"], rows)


def q_top_severe_communes(limit: int) -> None:
    rows = list_top_severe_communes(limit)
    print_table(["commune", "severe_accidents"], rows)


def q_risk_score_communes(limit: int) -> None:
    rows = compute_risk_score_by_commune(limit)
    print_table(["commune", "fatalities", "severe", "light", "risk_score"], rows)


def q_risk_score_commune(commune: str) -> None:
    fatalities, severe, light, risk_score = compute_commune_risk_score(commune)
    print_table(
        ["commune", "fatalities", "severe", "light", "risk_score"],
        [(commune, fatalities, severe, light, risk_score)],
    )


def q_trend_days(date_from: str, date_to: str, commune: Optional[str]) -> None:
    rows = compute_trend_days(date_from, date_to, commune)
    print_table(["day", "total"], rows)


def q_columns(schema: str, table: str) -> None:
    rows = fetch_table_columns(schema, table)
    print_table(["column_name", "data_type"], rows)


# ---------------------------------------------------------------------
# REPL (prompt-only)
# ---------------------------------------------------------------------

def run_chat() -> None:
    """Interactive console chat (prompt-only)."""
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

        # Fixed commands
        if low == "overview":
            q_overview()
            continue
        if low == "fatal_rate":
            q_fatal_rate()
            continue
        if low == "collisions":
            q_collisions()
            continue
        if low == "by_hour":
            q_by_hour()
            continue
        if low == "day_vs_night":
            q_day_vs_night()
            continue
        if low == "by_month":
            q_by_month()
            continue
        if low == "weekend_vs_week":
            q_weekend_vs_week()
            continue
        if low == "severe_by_age":
            q_severe_by_age()
            continue
        if low == "two_wheels_severe":
            q_two_wheels_severe()
            continue
        if low == "pedestrian_rate":
            q_pedestrian_rate()
            continue
        if low == "weather_impact":
            q_weather_impact()
            continue

        # Parameterized commands
        m = re.match(r"^top_communes\s+(\d+)$", q, re.IGNORECASE)
        if m:
            q_top_communes(int(m.group(1)))
            continue

        m = re.match(r"^stats\s+commune\s+(.+)$", q, re.IGNORECASE)
        if m:
            q_stats_commune(m.group(1).strip())
            continue

        m = re.match(r"^top_fatal_communes\s+(\d+)$", q, re.IGNORECASE)
        if m:
            q_top_fatal_communes(int(m.group(1)))
            continue

        m = re.match(r"^top_severe_communes\s+(\d+)$", q, re.IGNORECASE)
        if m:
            q_top_severe_communes(int(m.group(1)))
            continue

        m = re.match(r"^risk_score_communes\s+(\d+)$", q, re.IGNORECASE)
        if m:
            q_risk_score_communes(int(m.group(1)))
            continue

        m = re.match(r"^risk_score\s+commune\s+(.+)$", q, re.IGNORECASE)
        if m:
            q_risk_score_commune(m.group(1).strip())
            continue

        m = re.match(r"^gravity_values\s+(\d+)$", q, re.IGNORECASE)
        if m:
            q_gravity_values(int(m.group(1)))
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