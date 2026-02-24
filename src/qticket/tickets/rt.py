from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RT:
    rt_id: str
    train_id: str
    issued_at: float
