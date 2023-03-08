import pytest

from globus_compute_common.sdk_version_sharing import (
    GLOBUS_COMPUTE_VERSION_PREFIX,
    parse_version_number,
    user_agent_substring,
)


@pytest.mark.parametrize("version", ["foo", "1.0"])
def test_user_agent_substring(version: str):
    substring = user_agent_substring(version)
    assert GLOBUS_COMPUTE_VERSION_PREFIX in substring
    assert version in substring


@pytest.mark.parametrize("version", ["foo", "1.0"])
@pytest.mark.parametrize("template", ["{0}{1}", "bar/{0}{1}", "baz/{0}{1}/qux"])
def test_parse_version_number(version: str, template: str):
    user_agent_string = template.format(GLOBUS_COMPUTE_VERSION_PREFIX, version)
    assert parse_version_number(user_agent_string) == version


def test_parse_empty_version_number():
    assert parse_version_number("foo") is None
