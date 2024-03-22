"""Pydantic v2 provides access to the v1 API, enabling us to
continue using v1 while allowing users to install v2 as needed.
"""

try:
    from pydantic.v1 import *  # noqa: F401 F403
except ImportError:
    from pydantic import *  # noqa: F401 F403
