from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from . import accident_db as db


HELP_TEXT = """\
Road Safety interactive CLI (menu)

0) Retour menu principal
1) Overview (severity breakdown)
2) Fatal rate
3) Collisions (top)
4) Top communes
5) Columns (raw.accidents)
"""


@dataclass(frozen=True)
class MenuItem:
    key: str
    label: str
    action: Callable[[], None]


def _ask_int(prompt: str, default: Optional[int] = None) -> int:
    while True:
        raw = input(prompt).strip()
        if raw == "" and default is not None:
            return default
        try:
            return int(raw)
        except ValueError:
            print("Please enter an integer.")


def action_overview() -> None:
    rows = db.compute_severity_breakdown()
    db.print_table(["gravite_usager", "total"], rows)


def action_fatal_rate() -> None:
    rate, fatalities, total = db.compute_fatal_rate()
    db.print_table(["fatal_rate_%", "fatalities", "total"], [(rate, fatalities, total)])


def action_collisions() -> None:
    rows = db.list_collision_types()
    db.print_table(["type_collision", "total"], rows[:20])


def action_top_communes() -> None:
    n = _ask_int("How many communes (default 10)? ", default=10)
    rows = db.list_top_communes(n)
    db.print_table(["commune", "total"], rows)


def action_columns_raw_accidents() -> None:
    rows = db.fetch_table_columns("raw", "accidents")
    db.print_table(["column_name", "data_type"], rows)


def run_menu():
    print("=== Road Safety Interactive (Menu) ===")
    print("Type 'help' to show commands. Choose an option number.")

    items = [
        MenuItem("1", "Overview (severity breakdown)", action_overview),
        MenuItem("2", "Fatal rate", action_fatal_rate),
        MenuItem("3", "Collisions (top)", action_collisions),
        MenuItem("4", "Top communes", action_top_communes),
        MenuItem("5", "Columns (raw.accidents)", action_columns_raw_accidents),
    ]
    by_key = {it.key: it for it in items}

    while True:
        print("\nMenu:")
        print("  0) Retour menu principal")
        for it in items:
            print(f"  {it.key}) {it.label}")
        choice = input("> ").strip().lower()

        if choice == "0":
            print("Retour au menu principal.")
            return "menu"
        if choice in {"exit", "quit"}:
            return "quit"
        if choice in {"help", "h", "?"}:
            print(HELP_TEXT)
            continue

        item = by_key.get(choice)
        if not item:
            print("Unknown option. Type 'help' or choose a number.")
            continue

        try:
            item.action()
        except Exception as e:
            print(f"Error: {e}")
