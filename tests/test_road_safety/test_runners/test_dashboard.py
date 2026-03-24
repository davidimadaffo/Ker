"""Unit tests for road_safety.runners.dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Tuple

import pytest

import road_safety.runners.dashboard as dashboard


# ---------------------------------------------------------------------------
# Fake DB helpers
# ---------------------------------------------------------------------------

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
    return FakeConn(cursor_obj=FakeCursor(rows=rows, executed=[]))


# ---------------------------------------------------------------------------
# Tests for fetch_accidents_by_year
# ---------------------------------------------------------------------------

class TestFetchAccidentsByYear:
    def test_returns_year_and_count(self, monkeypatch):
        conn = make_fake_conn([("2021", 500), ("2022", 600)])

        def fake_establish():
            return conn

        monkeypatch.setattr(
            "road_safety.data_access.utils.establish_connection",
            fake_establish,
        )
        monkeypatch.setattr(dashboard, "_fetch_all", lambda q, p=(): [("2021", 500), ("2022", 600)])

        result = dashboard.fetch_accidents_by_year()

        assert result == [("2021", 500), ("2022", 600)]

    def test_sql_contains_year_grouping(self, monkeypatch):
        queries = []

        def capture_fetch(query, params=()):
            queries.append(query)
            return [("2021", 100)]

        monkeypatch.setattr(dashboard, "_fetch_all", capture_fetch)

        dashboard.fetch_accidents_by_year()

        assert queries
        assert "YYYY" in queries[0]
        assert "date_acc" in queries[0]


# ---------------------------------------------------------------------------
# Tests for fetch_accidents_by_commune
# ---------------------------------------------------------------------------

class TestFetchAccidentsByCommune:
    def test_returns_commune_and_count(self, monkeypatch):
        monkeypatch.setattr(dashboard, "_fetch_all", lambda q, p=(): [("Reims", 1200), ("Paris", 900)])

        result = dashboard.fetch_accidents_by_commune(limit=2)

        assert result == [("Reims", 1200), ("Paris", 900)]

    def test_limit_passed_to_query(self, monkeypatch):
        captured = {}

        def capture(query, params=()):
            captured["params"] = params
            return [("Reims", 1200)]

        monkeypatch.setattr(dashboard, "_fetch_all", capture)

        dashboard.fetch_accidents_by_commune(limit=5)

        assert captured["params"] == (5,)


# ---------------------------------------------------------------------------
# Tests for fetch_accidents_by_hour
# ---------------------------------------------------------------------------

class TestFetchAccidentsByHour:
    def test_returns_hour_and_count(self, monkeypatch):
        monkeypatch.setattr(dashboard, "_fetch_all", lambda q, p=(): [(8, 100), (17, 200)])

        result = dashboard.fetch_accidents_by_hour()

        assert result == [(8, 100), (17, 200)]

    def test_sql_extracts_hour(self, monkeypatch):
        queries = []

        def capture(query, params=()):
            queries.append(query)
            return [(8, 100)]

        monkeypatch.setattr(dashboard, "_fetch_all", capture)
        dashboard.fetch_accidents_by_hour()

        assert "EXTRACT(HOUR" in queries[0]
        assert "heure_acc" in queries[0]


# ---------------------------------------------------------------------------
# Tests for fetch_accidents_by_weather
# ---------------------------------------------------------------------------

class TestFetchAccidentsByWeather:
    def test_returns_weather_and_count(self, monkeypatch):
        monkeypatch.setattr(dashboard, "_fetch_all", lambda q, p=(): [("Normale", 500), ("Pluie", 300)])

        result = dashboard.fetch_accidents_by_weather()

        assert result == [("Normale", 500), ("Pluie", 300)]

    def test_sql_uses_cond_atmos(self, monkeypatch):
        queries = []

        def capture(query, params=()):
            queries.append(query)
            return [("Normale", 500)]

        monkeypatch.setattr(dashboard, "_fetch_all", capture)
        dashboard.fetch_accidents_by_weather()

        assert "cond_atmos" in queries[0]


# ---------------------------------------------------------------------------
# Tests for fetch_severity_distribution
# ---------------------------------------------------------------------------

class TestFetchSeverityDistribution:
    def test_returns_severity_and_count(self, monkeypatch):
        monkeypatch.setattr(
            dashboard, "_fetch_all", lambda q, p=(): [("Blessee Leger", 800), ("Tue", 50)]
        )

        result = dashboard.fetch_severity_distribution()

        assert result == [("Blessee Leger", 800), ("Tue", 50)]

    def test_sql_uses_gravite_usager(self, monkeypatch):
        queries = []

        def capture(query, params=()):
            queries.append(query)
            return [("Tue", 50)]

        monkeypatch.setattr(dashboard, "_fetch_all", capture)
        dashboard.fetch_severity_distribution()

        assert "gravite_usager" in queries[0]
