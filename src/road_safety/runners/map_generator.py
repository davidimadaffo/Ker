"""Interactive accident map generator.

Reads GPS coordinates from the database and produces a ``accidents_map.html``
file using *folium* (HTML/Leaflet.js).  No browser is required to generate the
file – the user can open it in any modern browser after running
``road-safety map``.

Falls back gracefully when *folium* is not installed, printing a helpful
error message instead of crashing the whole application.
"""

from __future__ import annotations

import os
from typing import Any

from ..data_access.utils import establish_connection


def fetch_coordinates(limit: int = 2000) -> list[tuple[float, float]]:
    """Return a list of (latitude, longitude) pairs from the database.

    Rows with NULL or out-of-range coordinates are excluded.
    """
    conn = establish_connection()
    if not conn:
        raise RuntimeError(
            "Database connection failed. Check DB_HOST / DB_PORT / credentials."
        )
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT latitude::float, longitude::float
            FROM raw.accidents
            WHERE latitude IS NOT NULL
              AND longitude IS NOT NULL
              AND latitude  BETWEEN -90  AND 90
              AND longitude BETWEEN -180 AND 180
            LIMIT %s;
            """,
            (limit,),
        )
        rows: list[Any] = cur.fetchall()
        cur.close()
        return [(float(lat), float(lon)) for lat, lon in rows]
    finally:
        conn.close()


def build_map(
    coordinates: list[tuple[float, float]],
    center: tuple[float, float] = (46.5, 2.5),
    zoom_start: int = 6,
) -> Any:
    """Build a *folium* Map object from a list of (lat, lon) coordinates.

    Parameters
    ----------
    coordinates:
        List of (latitude, longitude) tuples to plot as red circle markers.
    center:
        Initial map centre (defaults to metropolitan France).
    zoom_start:
        Initial zoom level.

    Returns
    -------
    A ``folium.Map`` instance.

    Raises
    ------
    ImportError
        If *folium* is not installed in the current environment.
    """
    try:
        import folium  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "The 'folium' package is required to generate maps.\n"
            "Install it with:  pip install folium"
        ) from exc

    accident_map = folium.Map(location=list(center), zoom_start=zoom_start)
    for lat, lon in coordinates:
        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color="red",
            fill=True,
            fill_opacity=0.6,
            tooltip=f"({lat:.4f}, {lon:.4f})",
        ).add_to(accident_map)
    return accident_map


def save_map(accident_map: Any, output_path: str) -> None:
    """Save a *folium* Map to *output_path*."""
    accident_map.save(output_path)


def generate_map(output_path: str = "accidents_map.html", limit: int = 2000) -> str:
    """Fetch coordinates from the DB and write an interactive HTML map.

    Parameters
    ----------
    output_path:
        Destination file path.  Defaults to ``accidents_map.html`` in the
        current working directory.
    limit:
        Maximum number of accidents to plot (prevents huge files).

    Returns
    -------
    The resolved *output_path* string.
    """
    coords = fetch_coordinates(limit)
    accident_map = build_map(coords)
    save_map(accident_map, output_path)
    return output_path


def run_map(output_path: str = "accidents_map.html", limit: int = 2000) -> None:
    """Entry point for the ``road-safety map`` command."""
    print(f"Fetching up to {limit} accident coordinates from the database…")
    try:
        path = generate_map(output_path=output_path, limit=limit)
        print(f"✅  Interactive map saved to: {os.path.abspath(path)}")
        print("Open the file in any browser to explore the accident locations.")
    except ImportError as exc:
        print(f"⚠️  {exc}")
    except RuntimeError as exc:
        print(f"⚠️  {exc}")
