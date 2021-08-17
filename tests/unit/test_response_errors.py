from funcx_common.response_errors import FuncxResponseError, UserUnauthenticated


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
