"""
Testing splitting the RPM filename
"""

from katprep.management.utilities import split_rpm_filename

import pytest


@pytest.mark.parametrize("filename, expected_result", [
    ("foo-1.0-1.i386.rpm", ("foo", "1.0", "1", "", "i386")),
    ("1:bar-9-123a.ia64.rpm", ("bar", "9", "123a", "1", "ia64")),
])
def test_splitting_rpm(filename, expected_result):
    assert expected_result == split_rpm_filename(filename)
