from __future__ import annotations

from qticket.protocol import errors
from qticket.tickets.revoke import RevocationList
from qticket.tickets.st import ST


def validate_st(st: ST, link_ctx: str, now_ts: float, revocations: RevocationList) -> str:
    if revocations.is_revoked(st.st_id):
        return errors.ERR_REVOKED
    if st.expires_at < now_ts:
        return errors.ERR_EXPIRED
    if st.link_ctx != link_ctx:
        return errors.ERR_BINDING_MISMATCH
    return errors.OK
