from __future__ import annotations

from qticket.schemes.ours_qticket.scheme import OursQTicketScheme
from qticket.schemes.base import RebindResult


class BaselineTicket2RttScheme(OursQTicketScheme):
    name = "baseline_ticket_2rtt"

    def rebind(self, train_id, st, link_ctx, challenge_opts):
        result: RebindResult = super().rebind(train_id, st, link_ctx, challenge_opts)
        result.rtt = 2
        result.msg_bytes = int(self.cfg.get("msg_bytes", 760))
        return result
