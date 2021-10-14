import json
from datetime import datetime, timedelta

import pytest

from katprep.host import Host, Erratum


def test_getting_custom_virt_name():
    host = Host("my.hostname", {"katprep_virt_name": "doge.coin.up"}, None)

    assert host.hostname != host.virtualisation_id
    assert host.virtualisation_id == "doge.coin.up"


def test_getting_virt_name():
    host = Host("my.hostname", {}, None)

    assert host.hostname == host.virtualisation_id
    assert host.virtualisation_id == "my.hostname"


def test_getting_custom_monitoring_id():
    host = Host("my.hostname", {"katprep_mon_name": "doge.coin.up"}, None)

    assert host.hostname != host.monitoring_id
    assert host.monitoring_id == "doge.coin.up"


def test_getting_monitoring_id():
    host = Host("my.hostname", {}, None)

    assert host.hostname == host.monitoring_id
    assert host.monitoring_id == "my.hostname"


def test_host_with_custom_location():
    host = Host("a", {}, "org", "my loc")

    assert host.location == "my loc"


@pytest.mark.parametrize(
    "first, second",
    [
        (Host("a", {}, "org a"), Host("a", {}, "org a")),
        pytest.param(
            Host("a", {}, "org a"),
            Host("b", {}, "org a"),
            marks=pytest.mark.xfail(reason="Different hostname"),
        ),
        pytest.param(
            Host("a", {"some": 1}, "org a"),
            Host("a", {"some": 2}, "org a"),
            marks=pytest.mark.xfail(reason="different params"),
        ),
        pytest.param(
            Host("a", {}, "org a"),
            Host("a", {}, "org b"),
            marks=pytest.mark.xfail(reason="different org"),
        ),
        pytest.param(
            Host("a", {"here": True}, "org a"),
            Host("b", {"There": False}, "org b"),
            marks=pytest.mark.xfail(reason="Different everything"),
        ),
        pytest.param(
            Host("a", {"here": True}, "org a", "loc a"),
            Host("b", {"There": False}, "org b", "fabolous location"),
            marks=pytest.mark.xfail(reason="Different everything with location"),
        ),
        pytest.param(
            Host("a", {}, "org a", "loc 1"),
            Host("a", {}, "org a"),
            marks=pytest.mark.xfail(reason="Missing location"),
        ),
        pytest.param(
            Host("a", {}, "org a", "loc 1"),
            Host("a", {}, "org a", "loc 2"),
            marks=pytest.mark.xfail(reason="Different location"),
        ),
        (
            Host("a", {}, "org", verifications={"a": True}),
            Host("a", {}, "org", verifications={"a": True})
        ),
        pytest.param(
            Host("a", {}, "org", verifications={"a": True}),
            Host("a", {}, "org", verifications={}),
            marks=pytest.mark.xfail(reason="Different verifications"),
        ),
        (
            Host("a", {}, "org", patches=["patch-123"]),
            Host("a", {}, "org", patches=["patch-123"]),
        ),
        pytest.param(
            Host("a", {}, "org", patches=["patch-1", "patch-2"]),
            Host("a", {}, "org", patches=["patch-3"]),
            marks=pytest.mark.xfail(reason="Different patches"),
        ),
        pytest.param(
            Host("a", {}, "org a", verifications=["patch-1", "patch-2"]),
            Host("b", {}, "org a", patches=["patch-3"]),
            marks=pytest.mark.xfail(reason="Some have params some patches"),
        ),
    ],
)
def test_host_comparison(first, second):
    assert first == second
    assert second == first


def test_host_comparison_with_different_patches(uyuni_erratum):
    erratas = []
    erratas2 = []
    for increment in range(5):
        e = Erratum.from_dict(uyuni_erratum)
        e.id = e.id + increment
        erratas.append(e)

        e = Erratum.from_dict(uyuni_erratum)
        e.id = e.id + increment
        if not increment:
            # Change the date on the first erratum
            e.updated_at += timedelta(minutes=10)
        erratas2.append(e)

    host1 = Host("a", {}, "org", patches=erratas)
    host2 = Host("a", {}, "org", patches=erratas2)

    assert host1 != host2


def test_creating_host_from_dict():
    host_dict = {
        "hostname": "some.hostname",
        "params": {},
        "organization": "Wayland Yutani",
    }
    expected_host = Host("some.hostname", {}, "Wayland Yutani")

    assert Host.from_dict(host_dict) == expected_host


@pytest.mark.parametrize(
    "hostkey",
    [
        "hostname",
        pytest.param(
            "nohostname", marks=pytest.mark.xfail(reason="invalid hostname key")
        ),
    ],
)
def test_creating_host_from_dict_requires_hostname(hostkey):
    host_dict = {
        hostkey: "some.hostname",
        "params": {},
        "organization": "Wayland Yutani",
    }
    expected_host = Host("some.hostname", {}, "Wayland Yutani")

    assert Host.from_dict(host_dict) == expected_host


def test_converting_host_to_dict():
    host = Host("my.hostname", {"some_param"}, "my orga")

    assert host.to_dict() == {
        "hostname": "my.hostname",
        "params": {"some_param"},
        "organization": "my orga",
        "cls": "host",
        "verifications": {},
        "patches": [],
    }


def test_host_json_conversion():
    original_dict = {
        "hostname": "hans.hubert",
        "params": {"sesame": "street"},
        "organization": "Funky town",
        "location": "Digges B",
        "cls": "host",
    }
    host = Host.from_dict(original_dict)
    new_dict = host.to_dict()

    del new_dict["verifications"]
    del new_dict["patches"]

    assert original_dict == new_dict


def test_host_json_conversion_with_verifications():
    original_dict = {
        "hostname": "hans.hubert",
        "params": {"sesame": "street"},
        "organization": "Funky town",
        "location": "Digges B",
        "cls": "host",
        "verifications": {"my_key": True},
    }
    host = Host.from_dict(original_dict)
    new_dict = host.to_dict()

    del new_dict["patches"]

    assert original_dict == new_dict


def test_host_json_conversion_with_verifications_and_patches():
    original_dict = {
        "hostname": "hans.hubert",
        "params": {"sesame": "street"},
        "organization": "Funky town",
        "location": "Digges B",
        "cls": "host",
        "verifications": {},
        "patches": [
            {'cls': 'erratum', 'type': 'testing', 'id': 1, 'name': 'katprep-12', 'summary': 'Nice updates', 'issued_at': '2021-09-16T00:00:00', 'updated_at': '2021-09-16T00:00:00', 'reboot_suggested': False},
            {'cls': 'erratum', 'type': 'testing', 'id': 2, 'name': 'katprep-34', 'summary': 'Noice noice noice', 'issued_at': '2021-08-16T00:00:00', 'updated_at': '2021-09-16T00:00:00', 'reboot_suggested': False}
        ],
    }

    host = Host.from_dict(original_dict)
    new_dict = host.to_dict()

    assert original_dict == new_dict


def test_host_str_contains_hostname():
    hostname = "some.hostname"
    assert hostname in str(Host(hostname, {}, None))


def test_host_representation():
    hostname = "some.hostname"
    params = {"my.param": "value"}
    org = "Wayland Yutani"
    loc = "Japan"
    verifications = {"snapshot": "1"}
    patches = ["patch-1"]

    host = Host(hostname, params, org, loc, verifications, patches)
    representation = repr(host)
    assert hostname in representation
    assert repr(params) in representation
    assert org in representation
    assert loc in representation
    assert repr(verifications) in representation
    assert repr(patches) in representation


def test_host_type_identifier():
    host = Host("bla", {}, None)
    assert host.type == "host"


def test_get_host_param():
    host = Host("bla", {"katprep_virt_type": "pyvmomi"}, None)

    assert host.get_param("katprep_virt_type") == "pyvmomi"


def test_get_host_param_ignores_empty_values():
    host = Host("bla", {"empty_value": ""}, None)

    assert host.get_param("empty_value") == None


def test_get_host_param_doesnt_fail_on_missing_value():
    host = Host("bla", {"empty_value": ""}, None)

    assert host.get_param("my_value") == None


def test_host_verification():
    host = Host("bla", {}, None, None)
    verified = host.get_verifications()
    assert not verified


def test_host_verification_by_value():
    host = Host("bla", {}, None, verifications={"virt_snapshort": True})
    verified = host.get_verifications()
    assert len(verified) == 1
    assert verified[0] == "virt_snapshort"
    assert host.get_verification("virt_snapshort") == True


@pytest.mark.parametrize(
    "key, value",
    [
        ("my_awesome_key", True),
        ("my_false_key", False),
    ],
)
def test_setting_verification(key, value):
    host = Host("bla", {}, None)
    host.set_verification(key, value)
    assert host.get_verification(key) == value


def test_getting_patches():
    orig_patches = ["patch-1", "patch-2"]
    host = Host("bla", {}, None, patches=orig_patches)

    patches = host.patches
    assert len(patches) == 2
    assert patches == orig_patches


def test_patches_are_empty_by_default():
    host = Host("bla", {}, None)

    assert not host.patches
    assert len(host.patches) == 0


@pytest.fixture
def uyuni_erratum():
    return {
        "id": 2075,
        "date": "8/27/21",
        "update_date": "8/27/21",
        "advisory_synopsis": "moderate: Security update for aws-cli, python-boto3, python-botocore, python-service_identity, python-trustme, python-urllib3",
        "advisory_type": "Security Advisory",
        "advisory_status": "stable",
        "advisory_name": "openSUSE-2021-1206",
    }


def test_creating_erratum_from_uyuni(uyuni_erratum):
    erratum = Erratum.from_uyuni(uyuni_erratum)

    assert erratum.id == 2075
    assert erratum.type == "Security Advisory"
    assert erratum.name == "openSUSE-2021-1206"
    assert erratum.issued_at == datetime(year=2021, month=8, day=27)
    assert erratum.updated_at == datetime(year=2021, month=8, day=27)
    assert erratum.summary.startswith("moderate: Security update")
    assert erratum.summary.endswith(", python-urllib3")
    assert not erratum.reboot_suggested


def test_creating_erratum_from_foreman():
    foreman_data = {
        "id": 9,
        "pulp_id": "FEDORA-EPEL-2020-68a03cd3b1",
        "title": "python-jmespath-0.9.4-2.el7",
        "errata_id": "FEDORA-EPEL-2020-68a03cd3b1",
        "issued": "2020-05-10",
        "updated": "2021-03-23",
        "severity": "None",
        "description": "Make jp.py use python2 again.",
        "solution": "",
        "summary": "python-jmespath-0.9.4-2.el7 bugfix update",
        "uuid": "FEDORA-EPEL-2020-68a03cd3b1",
        "name": "python-jmespath-0.9.4-2.el7",
        "type": "bugfix",
        "cves":
        [],
        "bugs":
        [
            {
                "bug_id": "1826380",
                "href": "https://bugzilla.redhat.com/show_bug.cgi?id=1826380"
            }
        ],
        "hosts_available_count": 1,
        "hosts_applicable_count": 1,
        "packages":
        [
            "python2-jmespath-0.9.4-2.el7.noarch",
            "python36-jmespath-0.9.4-2.el7.noarch",
            "python-jmespath-0.9.4-2.el7.src"
        ],
        "module_streams":
        [],
        "installable": True
    }

    erratum = Erratum.from_foreman(foreman_data)

    assert erratum.id == 9
    assert erratum.name == "FEDORA-EPEL-2020-68a03cd3b1"
    assert erratum.issued_at == datetime(year=2020, month=5, day=10)
    assert erratum.updated_at == datetime(year=2021, month=3, day=23)
    assert erratum.summary == "python-jmespath-0.9.4-2.el7 bugfix update"
    assert erratum.type == "bugfix"
    assert not erratum.reboot_suggested


def test_erratum_serialisation(uyuni_erratum):
    erratum = Erratum.from_dict(uyuni_erratum)

    erratum_dict = erratum.to_dict()
    erratum_from_dict = Erratum.from_dict(erratum_dict)
    erratum_dict2 = erratum_from_dict.to_dict()

    assert erratum_dict == erratum_dict2


def test_erratum_to_json(uyuni_erratum):
    erratum = Erratum.from_dict(uyuni_erratum)

    json.dumps(erratum.to_dict())


def test_erratum_comparison(uyuni_erratum):
    erratum1 = Erratum.from_dict(uyuni_erratum)
    erratum2 = Erratum.from_dict(uyuni_erratum)

    assert erratum1 == erratum2


def test_erratum_comparison_update_date(uyuni_erratum):
    erratum1 = Erratum.from_dict(uyuni_erratum)
    erratum2 = Erratum.from_dict(uyuni_erratum)
    assert erratum2.updated_at is not None
    erratum2.updated_at += timedelta(minutes=10)

    assert erratum1 != erratum2


def test_erratum_comparison_by_id(uyuni_erratum):
    erratum1 = Erratum.from_dict(uyuni_erratum)
    erratum2 = Erratum.from_dict(uyuni_erratum)
    erratum2.id = erratum1.id + 1

    assert erratum1 != erratum2