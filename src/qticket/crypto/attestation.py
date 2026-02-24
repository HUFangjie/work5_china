from __future__ import annotations


def check_attestation(train_id: str) -> bool:
    return train_id.startswith("tg-")
