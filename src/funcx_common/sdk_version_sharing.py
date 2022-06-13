"""
The funcx-sdk passes a user-agent header string containing sdk version information to
the web service, which logs that information. This is a small, centralized compatibility
module for that behavior.
"""

import typing as t

FUNCX_VERSION_PREFIX = "funcx-sdk-"


def user_agent_substring(version_number: str) -> str:
    return FUNCX_VERSION_PREFIX + version_number


def parse_version_number(user_agent_string: str) -> t.Optional[str]:
    for part in user_agent_string.split("/"):
        if part.startswith(FUNCX_VERSION_PREFIX):
            return part.replace(FUNCX_VERSION_PREFIX, "")
    return None
