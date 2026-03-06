import builtins
from dataclasses import dataclass
from typing import Any, List, Tuple

import pytest

import road_safety.runners.accident_chat as chat


# ---------------------------------------------------------------------
# Fake DB objects (no real PostgreSQL required)
# ---------------------------------------------------------------------

@dataclass
class FakeCursor:
    rows: List[Tuple[Any, ...]]
    executed: List[Tuple[str, tuple]]

    def execute(self, query: str, params: tuple = ()):
        self.executed.append((query, params))

    def fetchall(self):
        return self.rows

    def close(self):
        pass


@dataclass
class FakeConn:
    cursor_obj: FakeCursor

    def cursor(self):
        return self.cursor_obj

    def close(self):
        pass


def make_fake_conn(rows: List[Tuple[Any, ...]]):
    cur = FakeCursor(rows=rows, executed=[])
    return FakeConn(cursor_obj=cur)


# ---------------------------------------------------------------------
# Introspection tests
# ---------------------------------------------------------------------

class TestFetchTableColumns:
    def test_fetch_table_columns_executes_expected_sql(self, monkeypatch):
        conn = make_fake_conn([("col1", "text"), ("col2", "integer")])
        monkeypatch.setattr(chat, "establish_connection", lambda: conn)

        result = chat.fetch_table_columns("raw", "accidents")

        assert result == [("col1", "text"), ("col2", "integer")]
        assert len(conn.cursor_obj.executed) == 1
        sql, params = conn.cursor_obj.executed[0]
        assert "information_schema.columns" in sql
        assert params == ("raw", "accidents")


# ---------------------------------------------------------------------
# Compute/list function tests
# ---------------------------------------------------------------------

class TestComputeSeverityBreakdown:
    def test_compute_severity_breakdown_returns_typed_values(self, monkeypatch):
        conn = make_fake_conn([("Tué", 5), ("Blessé léger", 10)])
        monkeypatch.setattr(chat, "establish_connection", lambda: conn)

        rows = chat.compute_severity_breakdown()

        assert rows == [("Tué", 5), ("Blessé léger", 10)]
        sql, _ = conn.cursor_obj.executed[0]
        assert "GROUP BY" in sql
        assert "gravite_usager" in sql


class TestComputeFatalRate:
    def test_compute_fatal_rate_returns_tuple(self, monkeypatch):
        conn = make_fake_conn([(1.234, 7, 567)])
        monkeypatch.setattr(chat, "establish_connection", lambda: conn)

        rate, fatalities, total = chat.compute_fatal_rate()

        assert rate == 1.234
        assert fatalities == 7
        assert total == 567
        sql, _ = conn.cursor_obj.executed[0]
        assert "fatal_rate_percent" in sql or "ROUND" in sql


class TestListTopCommunes:
    def test_list_top_communes_uses_limit_param(self, monkeypatch):
        conn = make_fake_conn([("Paris", 100), ("Reims", 50)])
        monkeypatch.setattr(chat, "establish_connection", lambda: conn)

        rows = chat.list_top_communes(10)

        assert rows[0] == ("Paris", 100)
        sql, params = conn.cursor_obj.executed[0]
        assert "LIMIT %s" in sql
        assert params == (10,)


class TestComputeCommuneKpis:
    def test_compute_commune_kpis_filters_case_insensitive(self, monkeypatch):
        conn = make_fake_conn([(200, 3, 20)])
        monkeypatch.setattr(chat, "establish_connection", lambda: conn)

        total, fatalities, severe = chat.compute_commune_kpis("Paris")

        assert (total, fatalities, severe) == (200, 3, 20)
        sql, params = conn.cursor_obj.executed[0]
        assert "LOWER(commune) = LOWER(%s)" in sql
        assert params[-1] == "Paris"


class TestComputeRiskScoreByCommune:
    def test_compute_risk_score_by_commune_returns_expected_shape(self, monkeypatch):
        conn = make_fake_conn([("Paris", 3, 10, 20, 49)])
        monkeypatch.setattr(chat, "establish_connection", lambda: conn)

        rows = chat.compute_risk_score_by_commune(5)

        assert rows == [("Paris", 3, 10, 20, 49)]
        sql, params = conn.cursor_obj.executed[0]
        assert "risk_score" in sql
        assert params[-1] == 5


class TestComputeCommuneRiskScore:
    def test_compute_commune_risk_score_returns_tuple(self, monkeypatch):
        conn = make_fake_conn([(1, 2, 3, 10)])
        monkeypatch.setattr(chat, "establish_connection", lambda: conn)

        fatalities, severe, light, score = chat.compute_commune_risk_score("Paris")

        assert (fatalities, severe, light, score) == (1, 2, 3, 10)
        sql, params = conn.cursor_obj.executed[0]
        assert "WHERE LOWER(commune) = LOWER(%s)" in sql
        assert params[-1] == "Paris"


class TestComputeTrendDays:
    def test_compute_trend_days_without_commune(self, monkeypatch):
        conn = make_fake_conn([("2026-01-01", 10), ("2026-01-02", 12)])
        monkeypatch.setattr(chat, "establish_connection", lambda: conn)

        rows = chat.compute_trend_days("2026-01-01", "2026-01-31", None)

        assert rows == [("2026-01-01", 10), ("2026-01-02", 12)]
        sql, params = conn.cursor_obj.executed[0]
        assert params == ("2026-01-01", "2026-01-31")
        assert "GROUP BY" in sql

    def test_compute_trend_days_with_commune(self, monkeypatch):
        conn = make_fake_conn([("2026-01-01", 2)])
        monkeypatch.setattr(chat, "establish_connection", lambda: conn)

        rows = chat.compute_trend_days("2026-01-01", "2026-01-31", "Paris")

        assert rows == [("2026-01-01", 2)]
        sql, params = conn.cursor_obj.executed[0]
        assert params == ("2026-01-01", "2026-01-31", "Paris")
        assert "LOWER(commune) = LOWER(%s)" in sql


# ---------------------------------------------------------------------
# Wrapper (q_*) output tests (prints)
# ---------------------------------------------------------------------

class TestQFunctionsOutput:
    def test_q_overview_prints_table(self, monkeypatch, capsys):
        monkeypatch.setattr(chat, "compute_severity_breakdown", lambda: [("Tué", 1)])
        chat.q_overview()
        out = capsys.readouterr().out
        assert "gravite_usager" in out
        assert "Tué" in out

    def test_q_risk_score_commune_prints_table(self, monkeypatch, capsys):
        monkeypatch.setattr(chat, "compute_commune_risk_score", lambda _: (1, 2, 3, 10))
        chat.q_risk_score_commune("Paris")
        out = capsys.readouterr().out
        assert "risk_score" in out
        assert "Paris" in out


# ---------------------------------------------------------------------
# REPL routing tests (run_chat)
# ---------------------------------------------------------------------

class TestRunChatRouting:
    def test_run_chat_routes_fixed_commands(self, monkeypatch):
        called = {"overview": 0, "fatal": 0}

        monkeypatch.setattr(chat, "q_overview", lambda: called.__setitem__("overview", called["overview"] + 1))
        monkeypatch.setattr(chat, "q_fatal_rate", lambda: called.__setitem__("fatal", called["fatal"] + 1))

        inputs = iter(["overview", "fatal_rate", "exit"])
        monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

        chat.run_chat()

        assert called["overview"] == 1
        assert called["fatal"] == 1

    def test_run_chat_routes_parameterized_commands(self, monkeypatch):
        called = {
            "top": 0,
            "top_fatal": 0,
            "top_severe": 0,
            "top_risk": 0,
            "stats": 0,
            "risk_commune": 0,
            "trend": 0,
            "cols": 0,
        }

        monkeypatch.setattr(chat, "q_top_communes", lambda n: called.__setitem__("top", called["top"] + n))
        monkeypatch.setattr(chat, "q_top_fatal_communes", lambda n: called.__setitem__("top_fatal", called["top_fatal"] + n))
        monkeypatch.setattr(chat, "q_top_severe_communes", lambda n: called.__setitem__("top_severe", called["top_severe"] + n))
        monkeypatch.setattr(chat, "q_risk_score_communes", lambda n: called.__setitem__("top_risk", called["top_risk"] + n))
        monkeypatch.setattr(chat, "q_stats_commune", lambda c: called.__setitem__("stats", called["stats"] + (1 if c == "Paris" else 0)))
        monkeypatch.setattr(chat, "q_risk_score_commune", lambda c: called.__setitem__("risk_commune", called["risk_commune"] + (1 if c == "Paris" else 0)))
        monkeypatch.setattr(chat, "q_trend_days", lambda d1, d2, c: called.__setitem__("trend", called["trend"] + (1 if (d1, d2, c) == ("2026-01-01", "2026-01-31", "Paris") else 0)))
        monkeypatch.setattr(chat, "q_columns", lambda s, t: called.__setitem__("cols", called["cols"] + (1 if (s, t) == ("raw", "accidents") else 0)))

        inputs = iter([
            "top_communes 10",
            "top_fatal_communes 3",
            "top_severe_communes 5",
            "risk_score_communes 8",
            "stats commune Paris",
            "risk_score commune Paris",
            "trend_days 2026-01-01 2026-01-31 commune Paris",
            "columns raw accidents",
            "exit",
        ])
        monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

        chat.run_chat()

        assert called["top"] == 10
        assert called["top_fatal"] == 3
        assert called["top_severe"] == 5
        assert called["top_risk"] == 8
        assert called["stats"] == 1
        assert called["risk_commune"] == 1
        assert called["trend"] == 1
        assert called["cols"] == 1

    def test_run_chat_unknown_command_prints_message(self, monkeypatch, capsys):
        inputs = iter(["unknown_cmd", "exit"])
        monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

        chat.run_chat()
        out = capsys.readouterr().out
        assert "Unknown command" in out

    def test_run_chat_extended_disabled(self, monkeypatch, capsys):
        """Extended commands should be ignored when the flag is off."""
        monkeypatch.setenv("RS_ENABLE_EXTENDED", "0")
        inputs = iter(["top_fatal_communes 3", "risk_score_communes 5", "exit"])
        monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

        chat.run_chat()
        out = capsys.readouterr().out
        # each unrecognized command triggers the unknown message
        assert out.count("Unknown command") >= 2


# ---------------------------------------------------------------------
# Additional compute function tests for newer commands
# ---------------------------------------------------------------------

class TestComputeHourlyDistribution:
    def test_compute_hourly_distribution_executes_expected_sql(self, monkeypatch):
        conn = make_fake_conn([(0, 5), (1, 7)])
        monkeypatch.setattr(chat, "establish_connection", lambda: conn)

        rows = chat.compute_hourly_distribution()

        assert rows == [(0, 5), (1, 7)]
        sql, _ = conn.cursor_obj.executed[0]
        assert "EXTRACT" in sql and "NULLIF" in sql and "heure_acc" in sql


class TestComputeDayVsNightStats:
    def test_compute_day_vs_night_stats_executes_expected_sql(self, monkeypatch):
        conn = make_fake_conn([("DAY", 10, 2, 3)])
        monkeypatch.setattr(chat, "establish_connection", lambda: conn)

        rows = chat.compute_day_vs_night_stats()

        assert rows == [("DAY", 10, 2, 3)]
        sql, params = conn.cursor_obj.executed[0]
        assert "luminosite" in sql
        assert params == (chat.FATAL_LABEL, chat.FATAL_LABEL, chat.SEVERE_LABEL)


class TestComputeMonthlyDistribution:
    def test_compute_monthly_distribution_executes_expected_sql(self, monkeypatch):
        conn = make_fake_conn([("2026-01", 20)])
        monkeypatch.setattr(chat, "establish_connection", lambda: conn)

        rows = chat.compute_monthly_distribution()

        assert rows == [("2026-01", 20)]
        sql, _ = conn.cursor_obj.executed[0]
        assert "TO_CHAR" in sql and "YYYY-MM" in sql


class TestComputeWeekendSeverityGap:
    def test_compute_weekend_severity_gap_executes_expected_sql(self, monkeypatch):
        conn = make_fake_conn([("WEEKEND", 30, 5, 10)])
        monkeypatch.setattr(chat, "establish_connection", lambda: conn)

        rows = chat.compute_weekend_severity_gap()

        assert rows == [("WEEKEND", 30, 5, 10)]
        sql, params = conn.cursor_obj.executed[0]
        assert "EXTRACT(DOW" in sql or "WEEKEND" in sql
        assert params == (chat.FATAL_LABEL, chat.FATAL_LABEL, chat.SEVERE_LABEL)


class TestQWrapperAdditional:
    def test_q_by_hour_prints_table(self, monkeypatch, capsys):
        monkeypatch.setattr(chat, "compute_hourly_distribution", lambda: [(0, 1)])
        chat.q_by_hour()
        out = capsys.readouterr().out
        assert "hour" in out
        assert "0" in out

    def test_q_day_vs_night_prints_table(self, monkeypatch, capsys):
        monkeypatch.setattr(chat, "compute_day_vs_night_stats", lambda: [("DAY", 1, 0, 0)])
        chat.q_day_vs_night()
        out = capsys.readouterr().out
        assert "luminosite" in out
        assert "DAY" in out
