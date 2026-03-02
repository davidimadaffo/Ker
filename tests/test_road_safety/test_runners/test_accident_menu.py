import builtins

from road_safety.runners import accident_cli


def test_menu_quit_immediately(monkeypatch, capsys):
    inputs = iter(["0"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    accident_cli.run_menu()
    out = capsys.readouterr().out
    assert "Road Safety Interactive" in out
    assert "Bye." in out


def test_menu_overview_calls_action(monkeypatch, capsys):
    # Stub out the DB calls to avoid touching real Postgres in unit tests
    monkeypatch.setattr(accident_cli.db, "compute_severity_breakdown", lambda: [("X", 1)])
    monkeypatch.setattr(accident_cli.db, "print_table", lambda headers, rows: print("TABLE_OK"))

    inputs = iter(["1", "0"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    accident_cli.run_menu()
    out = capsys.readouterr().out
    assert "TABLE_OK" in out
