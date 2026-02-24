from qticket.schemes.registry import create_scheme


def test_scheme_registry_loads_ours():
    s = create_scheme('ours_qticket', {'name': 'ours_qticket'})
    assert s.name == 'ours_qticket'
