from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class RebindRequest:
    train_id: str
    st_id: str
    link_ctx: str
    nonce: str
    proof: str


@dataclass
class RebindResponse:
    accepted: bool
    error_code: str
    new_st_id: Optional[str] = None
