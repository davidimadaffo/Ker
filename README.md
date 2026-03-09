# Road Safety

A command-line analytical tool for exploring road accident data stored in a PostgreSQL database.

## Getting started

### Requirements

- Python 3.14+
- PostgreSQL database populated with accident data
- Docker Desktop (optional – for the bundled Compose stack)

### Installation

```bash
poetry install
```

### Running the application

```bash
# Start the interactive CLI (menu or free-command mode)
road-safety chat

# Print smart analytical insights (most dangerous hour, commune, weather…)
road-safety insights

# Generate an interactive HTML accident map (requires folium)
road-safety map
# Optional: custom output path and point limit
road-safety map accidents_map.html 5000

# Launch the Streamlit analytical dashboard (requires streamlit)
road-safety dashboard
```

You can also invoke the package directly:

```bash
python -m road_safety chat
python -m road_safety insights
```

### Optional dependencies

The map and dashboard commands require additional packages:

```bash
pip install folium          # for road-safety map
pip install streamlit       # for road-safety dashboard
```

These packages are intentionally optional – the core CLI works without them.

---

## Features

| Command | Description |
|---------|-------------|
| `road-safety chat` | Interactive REPL with free commands (`overview`, `top_communes 10`, `by_hour`, …) or a numbered menu |
| `road-safety insights` | 🚨 Automatic analytical insights: most dangerous hour, weather, commune, intersection |
| `road-safety map` | 🗺️ Generate an interactive Leaflet map (`accidents_map.html`) of accident locations |
| `road-safety dashboard` | 📊 Launch a Streamlit dashboard with bar charts (accidents by year, hour, severity, commune, weather) |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `accidents_db` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | *(empty)* | Database password |
| `RS_ENABLE_EXTENDED` | `0` | Set to `1` to enable extended chat commands |
| `ROAD_SAFETY_MODE` | *(ask)* | Force `menu` or `free` mode for `chat` |

## Running tests

```bash
pytest tests/
# or with coverage
pytest tests/ --cov=road_safety
```

## Project structure

```
src/road_safety/
├── main.py                    # CLI entry point
├── runners/
│   ├── accident_chat.py       # Free-command REPL
│   ├── accident_cli.py        # Numbered menu
│   ├── accident_analytics.py  # Additional analytics helpers
│   ├── accident_db.py         # DB query helpers used by the menu
│   ├── accident_explorer.py   # Data loading pipeline
│   ├── dashboard.py           # Streamlit dashboard
│   ├── insights.py            # Smart analytical insights CLI command
│   ├── map_generator.py       # Interactive HTML map generator
│   └── report_form.py         # Accident report submission form
├── data_access/               # Database connection & loaders
├── bootstrap/                 # Environment / seed helpers
└── config/                    # Settings (pydantic-settings)
```
