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
    container.save()

    new_container = AuthContainer(logging.DEBUG, temp_filename)
    creds = new_container.get_credential(hostname)
    assert creds.username == username
    assert creds.password == password


def test_reading_from_encrypted_file(temp_filename):
    key = 'hall0w3lt!'
    hostname = 'meinhost.some.domain'
    username = 'ingo'
    password = 'ebbelwoi'
    container = AuthContainer(logging.DEBUG, temp_filename, key)
    container.add_credentials(hostname, username, password)
    container.save()

    new_container = AuthContainer(logging.DEBUG, temp_filename, key)
    creds = new_container.get_credential(hostname)
    assert creds.username == username
    assert creds.password == password


def test_listing_hostnames(temp_filename):
    hostname = 'meinhost.some.domain'
    username = 'ingo'
    password = 'ebbelwoi'
    container = AuthContainer(logging.DEBUG, temp_filename)
    assert not container.get_hostnames()
    container.add_credentials(hostname, username, password)

    assert [hostname] == container.get_hostnames()
