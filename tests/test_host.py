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


def test_converting_host_to_dict():
    host = Host("my.hostname", {"some_param"}, "my orga")

    assert host.to_dict() == {
        "hostname": "my.hostname",
        "params": {"some_param"},
        "organisation": "my orga",
        "type": "host",
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

    assert original_dict == new_dict


def test_host_str_contains_hostname():
    hostname = "some.hostname"
    assert hostname in str(Host(hostname, {}, None))


def test_host_type_identifier():
    host = Host("bla", {}, None)
    assert host.type == "host"
