from qticket.schemes.registry import create_scheme


def test_replay_rejected_by_ours():
    s = create_scheme('ours_qticket', {'name': 'ours_qticket', 'msg_bytes': 100})
    s.bootstrap({})
    rt = s.issue_rt('tg-001')
    st = s.issue_st('tg-001', rt, 'ag1')
    res = s.rebind('tg-001', st, 'ag1', {'replay': True})
    assert res.accepted is False
