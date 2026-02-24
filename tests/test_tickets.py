import time

from qticket.protocol import errors
from qticket.tickets.revoke import RevocationList
from qticket.tickets.st import ST
from qticket.tickets.validate import validate_st


def test_ticket_validation_ok_and_revoked():
    rev = RevocationList()
    st = ST('st1', 'tg-001', 'ag1', time.time(), time.time() + 10)
    assert validate_st(st, 'ag1', time.time(), rev) == errors.OK
    rev.revoke('st1', time.time())
    assert validate_st(st, 'ag1', time.time(), rev) == errors.ERR_REVOKED
