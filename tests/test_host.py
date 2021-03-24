import pytest

from katprep.host import Host


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
    ],
)
def test_host_comparison(first, second):
    assert first == second
    assert second == first


def test_creating_host_from_dict():
    host_dict = {
        "hostname": "some.hostname",
        "params": {},
        "organisation": "Wayland Yutani",
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
        "organisation": "Wayland Yutani",
    }
    expected_host = Host("some.hostname", {}, "Wayland Yutani")

    assert Host.from_dict(host_dict) == expected_host


def test_converting_host_to_dict():
    host = Host("my.hostname", {"some_param"}, "my orga")

    assert host.to_dict() == {
        "hostname": "my.hostname",
        "params": {"some_param"},
        "organisation": "my orga",
        "type": "host",
        "verifications": {},
    }


def test_host_json_conversion():
    original_dict = {
        "hostname": "hans.hubert",
        "params": {"sesame": "street"},
        "organisation": "Funky town",
        "location": "Digges B",
        "type": "host",
    }
    host = Host.from_dict(original_dict)
    new_dict = host.to_dict()

    del new_dict["verifications"]

    assert original_dict == new_dict


def test_host_json_conversion_with_verifications():
    original_dict = {
        "hostname": "hans.hubert",
        "params": {"sesame": "street"},
        "organisation": "Funky town",
        "location": "Digges B",
        "type": "host",
        "verifications": {},
    }
    host = Host.from_dict(original_dict)
    new_dict = host.to_dict()

    assert original_dict == new_dict


def test_host_str_contains_hostname():
    hostname = "some.hostname"
    assert hostname in str(Host(hostname, {}, None))


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
