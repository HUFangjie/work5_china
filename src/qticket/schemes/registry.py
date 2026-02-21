from __future__ import annotations

from typing import Dict, Type

from qticket.schemes.base import Scheme
from qticket.schemes.baseline_full_reauth.scheme import BaselineFullReauthScheme
from qticket.schemes.baseline_qkd_vpn.scheme import BaselineQkdVpnScheme
from qticket.schemes.baseline_ticket_2rtt.scheme import BaselineTicket2RttScheme
from qticket.schemes.baseline_token_only.scheme import BaselineTokenOnlyScheme
from qticket.schemes.ours_qticket.scheme import OursQTicketScheme

SCHEME_REGISTRY: Dict[str, Type[Scheme]] = {
    OursQTicketScheme.name: OursQTicketScheme,
    BaselineFullReauthScheme.name: BaselineFullReauthScheme,
    BaselineTokenOnlyScheme.name: BaselineTokenOnlyScheme,
    BaselineTicket2RttScheme.name: BaselineTicket2RttScheme,
    BaselineQkdVpnScheme.name: BaselineQkdVpnScheme,
}


def create_scheme(name: str, cfg: dict) -> Scheme:
    if name not in SCHEME_REGISTRY:
        raise KeyError(f"unknown scheme: {name}")
    return SCHEME_REGISTRY[name](cfg)
