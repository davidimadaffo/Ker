import builtins
import os
import sys

from road_safety.runners.accident_chat import run_chat
from road_safety.runners.chanvre_report import run_chanvre_report

try:
    from road_safety.runners.accident_cli import run_menu
except Exception:  # pragma: no cover
    run_menu = None

_ORIGINAL_INPUT = builtins.input


def _choose_mode() -> str:
    forced = os.getenv("ROAD_SAFETY_MODE", "").strip().lower()
    if forced in {"menu", "free"}:
        return forced

    # If stdin isn't interactive (pytest), don't prompt unless input was monkeypatched by tests
    input_is_patched = builtins.input is not _ORIGINAL_INPUT
    if not sys.stdin.isatty() and not input_is_patched:
        return "free"

    while True:
        print("Choose a mode:")
        print("  1) Menu (options)")
        print("  2) Free commands (overview, top_communes 10, ...)")
        choice = builtins.input("> ").strip().lower()

        if choice in {"1", "menu", "m"}:
            return "menu"
        if choice in {"2", "free", "f", "commands", "cmd"}:
            return "free"

        print("Invalid choice. Please type 1 or 2.")


def main() -> int:
    args = sys.argv[1:]

    if args and args[0].lower() == "chanvre-report":
        output_path = args[1] if len(args) > 1 else None
        run_chanvre_report(output_path)
        return 0

    if args and args[0].lower() == "chat":
        mode = _choose_mode()

        if mode == "menu":
            if run_menu is None:
                print("Menu mode is not available in this environment.")
                return 1
            run_menu()
            return 0

        # mode == "free"
        run_chat()
        return 0

    print("Usage: road-safety chat | road-safety chanvre-report [output.pdf]")
    return 1
