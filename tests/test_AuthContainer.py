import logging
import os
import pytest
from katprep.AuthContainer import AuthContainer

# Auth file:
# * one encrypted
# * one not

@pytest.fixture
def temp_filename(tmp_path):
    yield os.path.join(tmp_path, 'auth-file')


def test_reading_from_unencrypted_file(temp_filename):
    hostname = 'meinhost.some.domain'
    username = 'ingo'
    password = 'ebbelwoi'
    container = AuthContainer(logging.DEBUG, temp_filename)
    container.add_credentials(hostname, username, password)

    assert container.CREDENTIALS
    creds = container.get_credential(hostname)
    assert creds[0] == username
    assert creds[1] == password
