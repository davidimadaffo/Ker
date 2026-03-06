import road_safety.data_access.utils as utils


def test_establish_connection_calls_env_loader(monkeypatch):
    called = {"ok": 0}

    # 1) Spy on env loader
    monkeypatch.setattr(utils, "load_dotenv_if_present", lambda: called.__setitem__("ok", called["ok"] + 1))

    # 2) Avoid real DB connection by patching psycopg2.connect to raise a controlled exception
    class DummyErr(Exception):
        pass

    def fake_connect(*args, **kwargs):
        raise DummyErr("no db in tests")

    monkeypatch.setattr(utils.psycopg2, "connect", fake_connect)

    # 3) Call function
    conn = utils.establish_connection()

    # 4) Assert loader called + connection handled
    assert called["ok"] == 1
    assert conn is None