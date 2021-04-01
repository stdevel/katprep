import os.path

import pytest

from katprep.host import Host
from katprep.reports import load_report, write_report


@pytest.fixture
def example_katello_report_path():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    filename = "errata-snapshot-report-10-20210324-1458.json"

    return os.path.join(test_dir, filename)


def test_loading_katello_report(example_katello_report_path):
    report = load_report(example_katello_report_path)

    assert report
    assert isinstance(report, dict)
    assert len(report) == 1

    for key, host in report.items():
        assert isinstance(host, Host)

        assert host.hostname == key
        assert host.hostname == "client.lab.giertz.com"

        assert host.organization == "Shitty Robots Corp"
        assert host.location == "Los Angeles"

        assert host.get_param("katprep_virt") == "vc6.lab.giertz.com"
        assert host.get_param("katprep_virt_type") == "pyvmomi"
        assert host.virtualisation_id == "Katello-Client"

        verifications = host.get_verifications()
        assert len(verifications) == 2

        assert host.get_verification("virt_snapshot") == True
        assert host.get_verification("virt_cleanup") == True

        patches = host.patches
        assert len(patches) == 1
        # TODO: Test the patch contents


@pytest.fixture
def temp_report_path(tmp_path):
    yield os.path.join(tmp_path, "report_file.json")


def test_writing_json_report(temp_report_path):
    report = {"myhost": {"params": {"hostname": "myhost"}}}

    write_report(temp_report_path, report)

    assert os.path.exists(temp_report_path)


def test_writing_reports_converts_hosts(temp_report_path):
    report = {"myhost": Host("myhost", {}, None)}

    write_report(temp_report_path, report)

    assert os.path.exists(temp_report_path)
