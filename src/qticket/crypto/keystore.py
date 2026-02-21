from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class KeyStore:
    keys: Dict[str, bytes] = field(default_factory=dict)

    def get_or_create(self, kid: str) -> bytes:
        if kid not in self.keys:
            self.keys[kid] = f"secret-{kid}".encode("utf-8")
        return self.keys[kid]
