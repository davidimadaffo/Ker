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
