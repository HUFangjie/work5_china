from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RevocationList:
    revoked: Dict[str, float] = field(default_factory=dict)

    def revoke(self, st_id: str, ts: float) -> None:
        self.revoked[st_id] = ts

    def is_revoked(self, st_id: str) -> bool:
        return st_id in self.revoked
