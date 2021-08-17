from funcx_common.response_errors import (
    FuncxResponseError,
    ResponseErrorCode,
    UserUnauthenticated,
)


def test_pack_error():
    data = UserUnauthenticated().pack()
    assert isinstance(data, dict)
    assert data["status"] == "Failed"
    assert data["code"] == 1
    assert data["error_args"] == []
    assert data["http_status_code"] == 401


def test_unpack_inverts_pack():
    packed = UserUnauthenticated().pack()
    assert isinstance(FuncxResponseError.unpack(packed), UserUnauthenticated)


def test_default_init_uses_reasonstr(monkeypatch):
    # ensure the class attr dict isn't changed by this test
    monkeypatch.setattr(FuncxResponseError, "_MAPPED_ERROR_CLASSES", {})

    class MyErr(FuncxResponseError):
        code = ResponseErrorCode.INTERNAL_ERROR
        http_status_code = 500

    err = MyErr("foo reason string")
    assert err.reason == "foo reason string"
    assert err.error_args == ["foo reason string"]


def test_default_error_stringification(monkeypatch):
    # ensure the class attr dict isn't changed by this test
    monkeypatch.setattr(FuncxResponseError, "_MAPPED_ERROR_CLASSES", {})

    class MyErr(FuncxResponseError):
        code = ResponseErrorCode.INTERNAL_ERROR
        http_status_code = 500

    err = MyErr("foo reason string")
    assert str(err) == err.reason

    err_repr = repr(err)
    assert err_repr.startswith("MyErr(")
    assert err_repr.endswith(")")
    for substr in [
        "reason='foo reason string'",
        f"code={ResponseErrorCode.INTERNAL_ERROR}",
        "http_status_code=500",
    ]:
        assert substr in err_repr


def test_unpack_on_well_formed_but_unrecognized_data():
    result = FuncxResponseError.unpack(
        {
            "status": "Failed",
            "code": 99999,
            "error_args": ["uncompromisingly quotidian"],
        }
    )
    assert isinstance(result, Exception)
    assert "web service failed for an unknown reason" in str(result)
    result = FuncxResponseError.unpack(
        {
            "status": "Failed",
            "code": 99999,
            "error_args": ["uncompromisingly quotidian"],
            "reason": "cosmic ray bit flip",
        }
    )
    assert isinstance(result, Exception)
    assert "web service responded with a failure - cosmic ray bit flip" in str(result)


def test_unpack_on_malformed_data():
    result = FuncxResponseError.unpack({})
    assert result is None
