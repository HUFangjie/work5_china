from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Dict


def kdf(secret: bytes, context: str) -> str:
    return hashlib.sha256(secret + context.encode("utf-8")).hexdigest()


def sign_payload(key: bytes, payload: str) -> str:
    sig = hmac.new(key, payload.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode("utf-8")


def verify_signature(key: bytes, payload: str, signature: str) -> bool:
    expected = sign_payload(key, payload)
    return hmac.compare_digest(expected, signature)


def stage_costs(cfg: Dict) -> Dict[str, float]:
    return {
        "verify_ticket_ms": float(cfg.get("verify_cost_ms", 1.0)),
        "revocation_lookup_ms": float(cfg.get("revocation_lookup_ms", 0.5)),
        "challenge_response_ms": float(cfg.get("challenge_cost_ms", 1.0)),
        "kdf_ms": 0.2,
        "restore_tunnel_ms": float(cfg.get("vpn_rebuild_ms", 2.0)),
    }
