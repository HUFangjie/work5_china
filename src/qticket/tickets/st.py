from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ST:
    st_id: str
    train_id: str
    link_ctx: str
    issued_at: float
    expires_at: float
