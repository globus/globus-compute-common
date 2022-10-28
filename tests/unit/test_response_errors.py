import uuid

import pytest

from funcx_common.response_errors import (
    AuthGroupNotFound,
    ContainerNotFound,
    EndpointAccessForbidden,
    EndpointAlreadyRegistered,
    EndpointLockedError,
    EndpointNotFound,
    EndpointOutdated,
    EndpointStatsError,
    ForwarderContactError,
    ForwarderRegistrationError,
    FunctionAccessForbidden,
    FunctionNotFound,
    FunctionNotPermitted,
    FuncxResponseError,
    InsufficientAuthScope,
    InternalError,
    InvalidAuthToken,
    InvalidUUID,
    LivenessStatsError,
    RequestKeyError,
    RequestMalformed,
    ResponseErrorCode,
    TaskGroupAccessForbidden,
    TaskGroupNotFound,
    TaskNotFound,
    UserNotFound,
    UserUnauthenticated,
)


def _check_pack_and_unpack(orig):
    packed = orig.pack()
    unpacked = FuncxResponseError.unpack(packed)
    assert isinstance(unpacked, orig.__class__)
    assert unpacked.reason == orig.reason


def test_pack_error():
    data = UserUnauthenticated().pack()
    assert isinstance(data, dict)
    assert data["status"] == "Failed"
    assert data["code"] == 1
    assert data["error_args"] == []
    assert data["http_status_code"] == 401


@pytest.mark.parametrize(
    "err_cls",
    [
        UserUnauthenticated,
        InvalidAuthToken,
        InsufficientAuthScope,
    ],
)
def test_unpack_inverts_pack_noargs(err_cls):
    _check_pack_and_unpack(err_cls())


@pytest.mark.parametrize(
    "err_cls",
    [
        UserNotFound,
        ForwarderRegistrationError,
        ForwarderContactError,
        RequestKeyError,
        RequestMalformed,
        InternalError,
        EndpointOutdated,
        InvalidUUID,
    ],
)
def test_unpack_inverts_pack_single_strarg(err_cls):
    _check_pack_and_unpack(err_cls("EXTERMINATE"))  # The Doctor


@pytest.mark.parametrize(
    "err_cls",
    [
        FunctionNotFound,
        EndpointNotFound,
        ContainerNotFound,
        TaskNotFound,
        AuthGroupNotFound,
        FunctionAccessForbidden,
        EndpointAccessForbidden,
        EndpointAlreadyRegistered,
        EndpointLockedError,
        TaskGroupNotFound,
        TaskGroupAccessForbidden,
    ],
)
def test_unpack_inverts_pack_single_uuidarg(err_cls):
    dummy_uuid = uuid.uuid1()
    _check_pack_and_unpack(err_cls(dummy_uuid))
    _check_pack_and_unpack(err_cls(str(dummy_uuid)))


def test_unpack_inverts_pack_function_not_permitted():
    dummy_uuid1 = uuid.uuid1()
    dummy_uuid2 = uuid.uuid1()
    _check_pack_and_unpack(FunctionNotPermitted(dummy_uuid1, dummy_uuid2))
    _check_pack_and_unpack(FunctionNotPermitted(str(dummy_uuid1), dummy_uuid2))
    _check_pack_and_unpack(FunctionNotPermitted(dummy_uuid1, str(dummy_uuid2)))
    _check_pack_and_unpack(FunctionNotPermitted(str(dummy_uuid1), str(dummy_uuid2)))


def test_unpack_inverts_pack_endpoint_stats():
    dummy_uuid = uuid.uuid1()
    _check_pack_and_unpack(
        EndpointStatsError(dummy_uuid, "You will be assimilated.")
    )  # The Enterprise
    _check_pack_and_unpack(
        EndpointStatsError(str(dummy_uuid), "You will be assimilated.")
    )


@pytest.mark.parametrize("status_code", [500, 400, 307])
def test_unpack_inverts_pack_liveness_stats(status_code):
    _check_pack_and_unpack(LivenessStatsError(status_code))
    _check_pack_and_unpack(LivenessStatsError(str(status_code)))


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
