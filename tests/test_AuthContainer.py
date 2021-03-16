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


@pytest.fixture
def hostname():
    return 'meinhost.some.domain'


@pytest.fixture
def username():
    return 'ingo'


@pytest.fixture
def password():
    return 'ebbelwoi'


def test_reading_from_unencrypted_file(temp_filename, hostname, username, password):
    container = AuthContainer(logging.DEBUG, temp_filename)
    container.add_credentials(hostname, username, password)
    container.save()

    new_container = AuthContainer(logging.DEBUG, temp_filename)
    creds = new_container.get_credential(hostname)
    assert creds.username == username
    assert creds.password == password


def test_reading_from_encrypted_file(temp_filename, hostname, username, password):
    key = 'hall0w3lt!'
    container = AuthContainer(logging.DEBUG, temp_filename, key)
    container.add_credentials(hostname, username, password)
    container.save()

    new_container = AuthContainer(logging.DEBUG, temp_filename, key)
    creds = new_container.get_credential(hostname)
    assert creds.username == username
    assert creds.password == password


def test_listing_hostnames(temp_filename, hostname, username, password):
    container = AuthContainer(logging.DEBUG, temp_filename)
    assert not container.get_hostnames()
    container.add_credentials(hostname, username, password)

    assert [hostname] == container.get_hostnames()


def test_retrieving_unknown_credential(temp_filename, hostname, username, password):
    container = AuthContainer(logging.DEBUG, temp_filename)
    container.add_credentials(hostname, username, password)

    assert None == container.get_credential('nothere'+ hostname)


def test_not_setting_empty_key(temp_filename):
    container = AuthContainer(logging.DEBUG, temp_filename)
    assert not container.is_encrypted()
    container.set_key("")
    assert not container.is_encrypted()


def test_setting_key(temp_filename):
    container = AuthContainer(logging.DEBUG, temp_filename)
    container.set_key("sosecret")
    assert container.is_encrypted()


def test_removing_credential(temp_filename, hostname, username, password):
    container = AuthContainer(logging.DEBUG, temp_filename)
    assert None == container.get_credential(hostname)

    container.add_credentials(hostname, username, password)
    assert container.get_credential(hostname)

    container.remove_credentials(hostname)
    assert None == container.get_credential(hostname)
