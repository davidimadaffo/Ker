from .runners import accident_explorer


def main() -> None:
    """Console entry point for Poetry script."""
    from .runners.accident_explorer import execute_analysis
    execute_analysis()


if __name__ == "__main__":
    main()