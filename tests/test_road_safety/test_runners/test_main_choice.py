import builtins
import road_safety.main as main_mod


def test_main_chat_choice_menu(monkeypatch):
    # Simulate "road-safety chat"
    monkeypatch.setattr(main_mod.sys, "argv", ["road-safety", "chat"])

    # Simulate choice "1" (menu)
    inputs = iter(["1"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    called = {"menu": 0, "free": 0}

    # Monkeypatch run_menu / run_chat
    monkeypatch.setattr(main_mod, "run_menu", lambda: called.__setitem__("menu", called["menu"] + 1))
    monkeypatch.setattr(main_mod, "run_chat", lambda: called.__setitem__("free", called["free"] + 1))

    rc = main_mod.main()
    assert rc == 0
    assert called["menu"] == 1
    assert called["free"] == 0


def test_main_chat_choice_free(monkeypatch):
    monkeypatch.setattr(main_mod.sys, "argv", ["road-safety", "chat"])

    inputs = iter(["2"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    called = {"menu": 0, "free": 0}
    monkeypatch.setattr(main_mod, "run_menu", lambda: called.__setitem__("menu", called["menu"] + 1))
    monkeypatch.setattr(main_mod, "run_chat", lambda: called.__setitem__("free", called["free"] + 1))

    rc = main_mod.main()
    assert rc == 0
    assert called["menu"] == 0
    assert called["free"] == 1
