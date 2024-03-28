"""Pydantic V2 provides access to the V1 API, enabling us to
continue using V1 while also supporting V2.
"""

try:
    from pydantic.v1 import *  # noqa: F401 F403
except ImportError:
    from pydantic import *  # type: ignore # noqa: F401 F403
