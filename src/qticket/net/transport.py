from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SimulatedLink:
    base_ms: float
    jitter_ms: float
    loss: float

    def one_way_ms(self) -> float:
        return self.base_ms + self.jitter_ms
