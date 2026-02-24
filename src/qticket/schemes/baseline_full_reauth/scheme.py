from __future__ import annotations

from qticket.schemes.ours_qticket.scheme import OursQTicketScheme
from qticket.schemes.base import RebindResult


class BaselineFullReauthScheme(OursQTicketScheme):
    name = "baseline_full_reauth"

    def rebind(self, train_id, st, link_ctx, challenge_opts):
        result: RebindResult = super().rebind(train_id, st, link_ctx, challenge_opts)
        result.rtt = int(self.cfg.get("rtt", 3))
        result.msg_bytes = int(self.cfg.get("msg_bytes", 1400))
        return result
