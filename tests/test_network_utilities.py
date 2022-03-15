import logging

import pytest
from katprep.network import is_ipv4

from .utilities import load_config


@pytest.mark.parametrize("address", [
    '192.168.0.1',
    '12.34.56.78',
    pytest.param('no', marks=pytest.mark.xfail),
    pytest.param('1.2.3', marks=pytest.mark.xfail),
    '1.2.3.4',
    pytest.param('1.2.3.4.5', marks=pytest.mark.xfail),
])
def test_ipv4_check(address):
    "Making sure we are able to identify an IPv4 address"
    assert is_ipv4(address)
