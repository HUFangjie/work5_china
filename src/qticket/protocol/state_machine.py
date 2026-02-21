from __future__ import annotations

from enum import Enum


class SessionState(str, Enum):
    INIT = "INIT"
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    REBINDING = "REBINDING"
    REVOKED = "REVOKED"
