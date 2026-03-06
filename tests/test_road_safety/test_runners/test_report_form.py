import builtins

import road_safety.runners.report_form as rf


def test_choose_from_list_selects_option(monkeypatch):
    inputs = iter(["2"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    out = rf.choose_from_list("Test", ["A", "B", "C"], allow_other=False)
    assert out == "B"


def test_run_report_form_builds_and_inserts(monkeypatch):
    # Mock dropdown options (no DB)
    monkeypatch.setattr(rf, "list_distinct", lambda col, limit=30: ["X", "Y"])

    # Capture inserted report
    captured = {}

    def fake_insert(r):
        captured["full_name"] = r.full_name
        captured["commune"] = r.commune
        captured["type_collision"] = r.type_collision

    monkeypatch.setattr(rf, "insert_report", fake_insert)

    # Inputs:
    # full_name
    # commune -> choose 1
    # type_collision -> choose 2
    # intersection -> choose 1
    # categorie_route -> choose 1
    # luminosite -> choose 1
    # cond_atmos -> choose 1
    # gravite -> choose 1
    # location_text
    # vehicle_type
    # notes
    inputs = iter([
        "Jean Dupont",
        "1", "2", "1", "1", "1", "1", "1",
        "Rue X",
        "VL",
        "RAS",
    ])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs))

    rf.run_report_form()

    assert captured["full_name"] == "Jean Dupont"
    assert captured["commune"] == "X"
    assert captured["type_collision"] == "Y"