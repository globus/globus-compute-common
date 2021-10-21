import pytest


@pytest.fixture(autouse=True)
def _unset_envvar_if_set(monkeypatch):
    # use monkeypatch.delenv to ensure that the env var is not set, preventing
    # test behaviors from changing
    # TODO: allow use of the redis URL env var to control test behavior
    monkeypatch.delenv("FUNCX_COMMON_REDIS_URL", raising=False)
