from katprep.host import from_dict, HostGroup, Host, Erratum, Upgrade

import pytest


def test_deserialise_host_from_dict():
    host = from_dict({"cls": "host", "hostname": "a", "params": {}, "organization": None})
    assert host.hostname == "a"
    assert isinstance(host, Host)


def test_deserialise_hostgroup_from_dict():
    group = from_dict({"cls": "hostgroup", "groupname": "b"})
    assert group.name == "b"
    assert isinstance(group, HostGroup)


def test_deserialise_erratum_from_dict():
    erratum = from_dict({
        "cls": 'erratum',
        'id': 9,
        'type': 'bugfix',
        'name': 'FEDORA-EPEL-2020-68a03cd3b1',
        'summary': 'python-jmespath-0.9.4-2.el7 bugfix update',
        'issued_at': '2020-05-10T00:00:00',
        'updated_at': '2021-03-23T00:00:00',
        'reboot_suggested': False
    })

    assert isinstance(erratum, Erratum)
    assert erratum.id == 9


def test_deserialise_upgrade_from_dict():
    upgrade = from_dict({"cls": "upgrade", "name": "tar"})

    assert isinstance(upgrade, Upgrade)
    assert upgrade.package_name == "tar"


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