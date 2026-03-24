"""Unit tests for road_safety.runners.map_generator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Tuple
from unittest.mock import MagicMock, patch

import pytest

import road_safety.runners.map_generator as map_gen


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
# Tests for fetch_coordinates
# ---------------------------------------------------------------------------

class TestFetchCoordinates:
    def test_returns_list_of_float_pairs(self, monkeypatch):
        conn = make_fake_conn([(48.85, 2.35), (43.30, 5.37)])
        monkeypatch.setattr(map_gen, "establish_connection", lambda: conn)

        result = map_gen.fetch_coordinates(limit=100)

        assert result == [(48.85, 2.35), (43.30, 5.37)]
        sql, params = conn.cursor_obj.executed[0]
        assert "latitude" in sql
        assert "longitude" in sql
        assert params == (100,)

    def test_returns_empty_list_when_no_rows(self, monkeypatch):
        conn = make_fake_conn([])
        monkeypatch.setattr(map_gen, "establish_connection", lambda: conn)

        result = map_gen.fetch_coordinates()

        assert result == []

    def test_raises_on_connection_failure(self, monkeypatch):
        monkeypatch.setattr(map_gen, "establish_connection", lambda: None)

        with pytest.raises(RuntimeError, match="Database connection failed"):
            map_gen.fetch_coordinates()

    def test_filters_null_coordinates_via_sql(self, monkeypatch):
        conn = make_fake_conn([])
        monkeypatch.setattr(map_gen, "establish_connection", lambda: conn)

        map_gen.fetch_coordinates()

        sql, _ = conn.cursor_obj.executed[0]
        assert "IS NOT NULL" in sql
        assert "BETWEEN" in sql


# ---------------------------------------------------------------------------
# Tests for build_map
# ---------------------------------------------------------------------------

class TestBuildMap:
    def test_raises_import_error_when_folium_missing(self, monkeypatch):
        import builtins
        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "folium":
                raise ImportError("No module named 'folium'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        with pytest.raises(ImportError, match="folium"):
            map_gen.build_map([(48.85, 2.35)])

    def test_builds_map_with_folium(self, monkeypatch):
        mock_marker = MagicMock()
        mock_map_instance = MagicMock()
        mock_folium = MagicMock()
        mock_folium.Map.return_value = mock_map_instance
        mock_folium.CircleMarker.return_value = mock_marker

        with patch.dict("sys.modules", {"folium": mock_folium}):
            result = map_gen.build_map([(48.85, 2.35), (43.30, 5.37)])

        mock_folium.Map.assert_called_once_with(location=[46.5, 2.5], zoom_start=6)
        assert mock_folium.CircleMarker.call_count == 2
        assert result is mock_map_instance


# ---------------------------------------------------------------------------
# Tests for save_map
# ---------------------------------------------------------------------------

class TestSaveMap:
    def test_calls_save_on_map(self):
        mock_map = MagicMock()
        map_gen.save_map(mock_map, "/tmp/test_map.html")
        mock_map.save.assert_called_once_with("/tmp/test_map.html")


# ---------------------------------------------------------------------------
# Tests for generate_map
# ---------------------------------------------------------------------------

class TestGenerateMap:
    def test_generate_map_calls_pipeline(self, monkeypatch):
        called = {}

        monkeypatch.setattr(map_gen, "fetch_coordinates", lambda limit: [(1.0, 2.0)])
        monkeypatch.setattr(
            map_gen,
            "build_map",
            lambda coords: called.__setitem__("map", True) or MagicMock(),
        )
        monkeypatch.setattr(map_gen, "save_map", lambda m, p: called.__setitem__("saved", p))

        result = map_gen.generate_map(output_path="/tmp/out.html", limit=50)

        assert result == "/tmp/out.html"
        assert called.get("saved") == "/tmp/out.html"


# ---------------------------------------------------------------------------
# Tests for run_map
# ---------------------------------------------------------------------------

class TestRunMap:
    def test_run_map_prints_success(self, monkeypatch, capsys):
        monkeypatch.setattr(map_gen, "generate_map", lambda output_path, limit: output_path)

        map_gen.run_map(output_path="/tmp/accidents_map.html", limit=100)

        out = capsys.readouterr().out
        assert "accidents_map.html" in out

    def test_run_map_handles_import_error(self, monkeypatch, capsys):
        monkeypatch.setattr(
            map_gen,
            "generate_map",
            lambda **kwargs: (_ for _ in ()).throw(ImportError("folium not installed")),
        )

        map_gen.run_map()

        out = capsys.readouterr().out
        assert "folium" in out.lower() or "⚠️" in out

    def test_run_map_handles_runtime_error(self, monkeypatch, capsys):
        monkeypatch.setattr(
            map_gen,
            "generate_map",
            lambda **kwargs: (_ for _ in ()).throw(RuntimeError("DB error")),
        )

        map_gen.run_map()

        out = capsys.readouterr().out
        assert "⚠️" in out
