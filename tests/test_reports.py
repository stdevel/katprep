import os.path
from datetime import datetime

import pytest

from katprep.host import Host, Erratum
from katprep.reports import load_report, write_report, is_valid_report


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
        erratum = patches[0]
        assert isinstance(erratum, Erratum)
        assert erratum.id == 9
        assert erratum.name == "FEDORA-EPEL-2020-68a03cd3b1"
        assert erratum.summary == "python-jmespath-0.9.4-2.el7 bugfix update"
        assert not erratum.reboot_suggested
        assert erratum.issued_at == datetime(year=2020, month=5, day=10)
        assert erratum.updated_at == datetime(year=2021, month=3, day=23)


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


def test_katello_report_validation(example_katello_report_path):
    assert is_valid_report(example_katello_report_path)


def test_writing_valid_reports(temp_report_path):
    report = {"myhost": Host("myhost", {}, None)}

    write_report(temp_report_path, report)
    assert is_valid_report(temp_report_path)

    loaded_report = load_report(temp_report_path)
    assert report == loaded_report


@pytest.fixture
def example_uyuni_report_path():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    filename = "errata-snapshot-report-10-20210910-1415.json"

    return os.path.join(test_dir, filename)


def test_reading_uyuni_snapshot_report(example_uyuni_report_path):
    report = load_report(example_uyuni_report_path)
    assert report
    assert isinstance(report, dict)
    assert len(report) == 1

    for key, host in report.items():
        assert isinstance(host, Host)

        assert host.hostname == "uyuni-client.labor.testdomain"
        assert host.management_id == 1000010000

        assert host.organization == "Demo"
        assert host.location == "Demo"

        assert host.get_param("katprep_virt") == "vc6.labor.testdomain"
        assert host.get_param("katprep_virt_type") == "pyvmomi"
        assert host.virtualisation_id == "Uyuni-Client"

        verifications = host.get_verifications()
        assert len(verifications) == 0

        patches = host.patches
        assert len(patches) == 3
        for patch in patches:
            assert isinstance(patch, Erratum)
        # TODO: Test the patch contents


def test_uyuni_report_validation(example_uyuni_report_path):
    assert is_valid_report(example_uyuni_report_path)
