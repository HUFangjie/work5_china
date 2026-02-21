from __future__ import annotations

from qticket.protocol import errors
from qticket.schemes.ours_qticket.scheme import OursQTicketScheme
from qticket.schemes.base import RebindResult


class BaselineTokenOnlyScheme(OursQTicketScheme):
    name = "baseline_token_only"

    def rebind(self, train_id, st, link_ctx, challenge_opts):
        if challenge_opts.get("impersonation") or challenge_opts.get("replay"):
            # weak baseline: some attacks pass
            return RebindResult(True, errors.OK, st, 1, int(self.cfg.get("msg_bytes", 320)))
        return super().rebind(train_id, st, link_ctx, challenge_opts)
