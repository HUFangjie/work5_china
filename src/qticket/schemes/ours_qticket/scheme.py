from __future__ import annotations

import time

from qticket.common.ids import new_id
from qticket.protocol import errors
from qticket.schemes.base import RebindResult, Scheme
from qticket.tickets.revoke import RevocationList
from qticket.tickets.rt import RT
from qticket.tickets.st import ST
from qticket.tickets.validate import validate_st


class OursQTicketScheme(Scheme):
    name = "ours_qticket"

    def bootstrap(self, context: dict) -> None:
        self.revocations: RevocationList = context.setdefault("revocations", RevocationList())

    def issue_rt(self, train_id: str) -> RT:
        return RT(new_id("rt"), train_id, time.time())

    def issue_st(self, train_id: str, rt: RT, link_ctx: str) -> ST:
        now = time.time()
        return ST(new_id("st"), train_id, link_ctx, now, now + 180)

    def rebind(self, train_id: str, st: ST, link_ctx: str, challenge_opts: dict) -> RebindResult:
        status = validate_st(st, st.link_ctx, time.time(), self.revocations)
        if status != errors.OK:
            return RebindResult(False, status, None, 1, int(self.cfg.get("msg_bytes", 680)))
        if challenge_opts.get("impersonation"):
            return RebindResult(False, errors.ERR_IMPERSONATION, None, 1, int(self.cfg.get("msg_bytes", 680)))
        if challenge_opts.get("wrong_binding") and link_ctx != st.link_ctx:
            return RebindResult(False, errors.ERR_BINDING_MISMATCH, None, 1, int(self.cfg.get("msg_bytes", 680)))
        if challenge_opts.get("replay"):
            return RebindResult(False, errors.ERR_REPLAY, None, 1, int(self.cfg.get("msg_bytes", 680)))
        new_st = ST(new_id("st"), train_id, link_ctx, time.time(), time.time() + 180)
        return RebindResult(True, errors.OK, new_st, 1, int(self.cfg.get("msg_bytes", 680)))

    def verify_and_accept(self, request: dict):
        accepted = request.get("proof_ok", True)
        return accepted, (errors.OK if accepted else errors.ERR_INVALID_TICKET), None
