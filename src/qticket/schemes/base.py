from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple

from qticket.tickets.rt import RT
from qticket.tickets.st import ST


@dataclass
class RebindResult:
    accepted: bool
    error_code: str
    new_st: Optional[ST]
    rtt: int
    msg_bytes: int


class Scheme(ABC):
    name: str

    def __init__(self, cfg: dict):
        self.cfg = cfg

    @abstractmethod
    def bootstrap(self, context: dict) -> None:
        ...

    @abstractmethod
    def issue_rt(self, train_id: str) -> RT:
        ...

    @abstractmethod
    def issue_st(self, train_id: str, rt: RT, link_ctx: str) -> ST:
        ...

    @abstractmethod
    def rebind(self, train_id: str, st: ST, link_ctx: str, challenge_opts: dict) -> RebindResult:
        ...

    @abstractmethod
    def verify_and_accept(self, request: dict) -> Tuple[bool, str, Optional[ST]]:
        ...
