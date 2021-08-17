from funcx_common.response_errors import UserUnauthenticated


def test_pack_error():
    data = UserUnauthenticated().pack()
    assert isinstance(data, dict)
    assert data["status"] == "Failed"
    assert data["code"] == 1
    assert data["error_args"] == []
    assert data["http_status_code"] == 401
