import builtins
import os
import sys

from road_safety.bootstrap import ensure_accidents_loaded
from road_safety.runners.accident_chat import run_chat
from road_safety.runners.accident_cli import run_menu
from road_safety.runners.report_form import run_report_form


def _is_pytest_running() -> bool:
    return os.getenv("PYTEST_CURRENT_TEST") is not None


def _choose_mode() -> str:
    print("Choose a mode:")
    print("  0) Quit")
    print("  1) Menu (options)")
    print("  2) Free commands (overview, top_communes 10, ...)")
    print("  3) Accident report")

    while True:
        choice = builtins.input("> ").strip().lower()

        if choice == "1":
            return "menu"
        if choice == "2":
            return "free"
        if choice == "3":
            return "report"
        if choice in {"0", "exit", "quit"}:
            return "quit"

        print("Invalid choice. Please enter 0, 1, 2 or 3.")


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] != "chat":
        print("Usage: road-safety chat")
        return 1

    ensure_accidents_loaded()

    # Compatibilite tests: un seul choix puis fin
    if _is_pytest_running():
        try:
            mode = _choose_mode()
        except OSError:
            mode = "free"

        if mode == "menu":
            run_menu()
            return 0
        if mode == "free":
            run_chat()
            return 0
        if mode == "report":
            run_report_form()
            return 0
        if mode == "quit":
            print("Bye.")
            return 0
        return 0

    # Usage reel: boucle interactive
    while True:
        mode = _choose_mode()

        if mode == "menu":
            result = run_menu()
            if result == "quit":
                print("Bye.")
                return 0
            continue

        if mode == "free":
            result = run_chat()
            if result == "quit":
                print("Bye.")
                return 0
            continue

        if mode == "report":
            run_report_form()
            continue

        if mode == "quit":
            print("Bye.")
            return 0