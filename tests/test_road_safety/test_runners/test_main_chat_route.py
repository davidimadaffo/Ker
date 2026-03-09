import road_safety.main as main_mod


def test_main_chat_routes_to_chat(monkeypatch):
    called = {"ok": False}

    def fake_run_chat():
        called["ok"] = True

    monkeypatch.setattr(main_mod, "run_chat", fake_run_chat)
    monkeypatch.setattr(main_mod.sys, "argv", ["road-safety", "chat"])

    rc = main_mod.main()
    assert rc == 0
    assert called["ok"] is True


def test_main_insights_routes_to_insights(monkeypatch):
    called = {"ok": False}

    monkeypatch.setattr(main_mod, "run_insights", lambda: called.__setitem__("ok", True))
    monkeypatch.setattr(main_mod.sys, "argv", ["road-safety", "insights"])

    rc = main_mod.main()
    assert rc == 0
    assert called["ok"] is True


def test_main_map_routes_to_map(monkeypatch):
    called = {}

    monkeypatch.setattr(
        main_mod,
        "run_map",
        lambda output_path, limit: called.__setitem__("args", (output_path, limit)),
    )
    monkeypatch.setattr(main_mod.sys, "argv", ["road-safety", "map"])

    rc = main_mod.main()
    assert rc == 0
    assert called["args"] == ("accidents_map.html", 2000)


def test_main_map_accepts_custom_path_and_limit(monkeypatch):
    called = {}

    monkeypatch.setattr(
        main_mod,
        "run_map",
        lambda output_path, limit: called.__setitem__("args", (output_path, limit)),
    )
    monkeypatch.setattr(main_mod.sys, "argv", ["road-safety", "map", "/tmp/my.html", "500"])

    rc = main_mod.main()
    assert rc == 0
    assert called["args"] == ("/tmp/my.html", 500)


def test_main_dashboard_routes_to_dashboard(monkeypatch):
    called = {"ok": False}

    monkeypatch.setattr(main_mod, "run_dashboard", lambda: called.__setitem__("ok", True))
    monkeypatch.setattr(main_mod.sys, "argv", ["road-safety", "dashboard"])

    rc = main_mod.main()
    assert rc == 0
    assert called["ok"] is True


def test_main_no_args_returns_error(monkeypatch, capsys):
    monkeypatch.setattr(main_mod.sys, "argv", ["road-safety"])

    rc = main_mod.main()

    assert rc == 1
    out = capsys.readouterr().out
    assert "Usage" in out


def test_main_unknown_command_returns_error(monkeypatch, capsys):
    monkeypatch.setattr(main_mod.sys, "argv", ["road-safety", "nonexistent"])

    rc = main_mod.main()

    assert rc == 1
    out = capsys.readouterr().out
    assert "Unknown command" in out
