from katprep.host import from_dict, HostGroup, Host

import pytest


def test_deserialise_host_from_dict():
    host = from_dict({"cls": "host", "hostname": "a", "params": {}, "organization": None})
    assert host.hostname == "a"
    assert isinstance(host, Host)


def test_deserialise_hostgroup_from_dict():
    group = from_dict({"cls": "hostgroup", "groupname": "b"})
    assert group.name == "b"
    assert isinstance(group, HostGroup)


@pytest.mark.parametrize("param", [1, "something"])
def test_converting_unexpected_type_fails(param):
    with pytest.raises(TypeError):
        from_dict(param)


def test_converting_expects_type_key():
    with pytest.raises(ValueError):
        from_dict({"no": "matching_key"})


def test_converting_unexpected_type():
    with pytest.raises(ValueError):
        from_dict({"cls": "dontexist"})