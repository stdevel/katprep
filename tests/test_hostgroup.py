import pytest

from katprep.host import HostGroup


@pytest.mark.parametrize(
    "first, second",
    [
        (HostGroup("a"), HostGroup("a")),
        pytest.param(
            HostGroup("a"),
            HostGroup("b"),
            marks=pytest.mark.xfail(reason="Different groupname"),
        ),
    ],
)
def test_hostgroup_comparison(first, second):
    assert first == second
    assert second == first


def test_hostgroup_monitoring_id():
    group = HostGroup("meine_gruppe")
    assert group.monitoring_id == "meine_gruppe"


def test_hostgroup_dict_conversion():
    original_dict = {"groupname": "Blargh", "type": "hostgroup"}
    group = HostGroup.from_dict(original_dict)

    assert group.to_dict() == original_dict


def test_groupname_in_str():
    groupname = "ABC"
    group = HostGroup(groupname)
    assert groupname in str(group)


def test_group_type_identifier():
    group = HostGroup("asdf")
    assert group.type == "hostgroup"
