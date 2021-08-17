import typing as t

from .constants import HTTPStatusCode, ResponseErrorCode


class FuncxResponseError(Exception):
    """Base class for all web service response exceptions"""

    _MAPPED_ERROR_CLASSES: t.Dict[ResponseErrorCode, t.Type["FuncxResponseError"]] = {}
    code: t.ClassVar[ResponseErrorCode]
    http_status_code: t.ClassVar[HTTPStatusCode]
    error_args: t.List[t.Any]
    reason: str

    def __init_subclass__(cls, **kwargs: t.Any) -> None:
        FuncxResponseError._MAPPED_ERROR_CLASSES[cls.code] = cls

    def __init__(self, reason: str) -> None:
        self.error_args = [reason]
        self.reason = reason

    def __str__(self) -> str:
        return self.reason

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            + ",".join(
                [
                    f"reason='{self.reason}'",
                    f"code={self.code}",
                    f"http_status_code={self.http_status_code}",
                    f"error_args={self.error_args}",
                ]
            )
            + ")"
        )

    def pack(self) -> t.Dict[str, t.Any]:
        return {
            "status": "Failed",
            "code": int(self.code),
            "error_args": self.error_args,
            "reason": self.reason,
            "http_status_code": int(self.http_status_code),
        }

    @classmethod
    def unpack(cls, res_data: t.Dict[str, t.Any]) -> t.Optional[Exception]:
        if "status" in res_data and res_data["status"] == "Failed":
            if (
                "code" in res_data
                and res_data["code"] != 0
                and "error_args" in res_data
            ):
                # if the response error code is not recognized here because the
                # user is not using the latest SDK version, an exception will occur
                # here which we will pass in order to give the user a generic
                # exception below
                try:
                    res_error_code = ResponseErrorCode(res_data["code"])
                except ValueError:
                    pass
                else:
                    error_class = FuncxResponseError._MAPPED_ERROR_CLASSES.get(
                        res_error_code
                    )
                    if error_class is not None:
                        return error_class(*res_data["error_args"])

            # this is useful for older SDK versions to be compatible with a newer web
            # service: if the SDK does not recognize an error code, it creates a generic
            # exception with the human-readable error reason that was sent
            if "reason" in res_data:
                return Exception(
                    f"The web service responded with a failure - {res_data['reason']}"
                )

            return Exception("The web service failed for an unknown reason")

        return None
