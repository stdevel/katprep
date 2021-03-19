import logging
import os
import os.path
import pytest
from katprep.AuthContainer import AuthContainer, ContainerException

# Auth file:
# * one encrypted
# * one not


@pytest.fixture
def temp_filename(tmp_path):
    yield os.path.join(tmp_path, "auth-file")


@pytest.fixture
def hostname():
    return "meinhost.some.domain"


@pytest.fixture
def username():
    return "ingo"


@pytest.fixture
def password():
    return "ebbelwoi"


def test_reading_from_unencrypted_file(temp_filename, hostname, username, password):
    container = AuthContainer(logging.DEBUG, temp_filename)
    container.add_credentials(hostname, username, password)
    container.save()

    new_container = AuthContainer(logging.DEBUG, temp_filename)
    creds = new_container.get_credential(hostname)
    assert creds.username == username
    assert creds.password == password


def test_reading_from_encrypted_file(temp_filename, hostname, username, password):
    key = "hall0w3lt!"
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

    assert None == container.get_credential("nothere" + hostname)


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


@pytest.fixture
def unencrypted_py2_file():
    test_dir = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(test_dir, "container-py2-unencrypted.auth")


def test_importing_unencrypted_python_2_file(unencrypted_py2_file):
    container = AuthContainer(logging.DEBUG, unencrypted_py2_file)

    hostnames = container.get_hostnames()
    assert 1 == len(hostnames)

    creds = container.get_credential(hostnames[0])
    assert creds.username == "username"
    assert creds.password == "password"


@pytest.fixture
def encrypted_py2_file():
    test_dir = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(test_dir, "container-py2.auth")


def test_importing_encrypted_python_2_file(encrypted_py2_file):
    filename = unencrypted_py2_file
    container = AuthContainer(logging.DEBUG, encrypted_py2_file, "test123")

    hostnames = container.get_hostnames()
    assert 1 == len(hostnames)

    creds = container.get_credential(hostnames[0])
    assert creds.username == "username"
    assert creds.password == "password"


def test_import_encrypted_python_2_file_with_wrong_keyword(encrypted_py2_file):
    container = AuthContainer(logging.DEBUG, encrypted_py2_file, "fakepassword")

    hostnames = container.get_hostnames()
    assert len(hostnames) >= 1

    with pytest.raises(ContainerException):
        container.get_credential(hostnames[0])


@pytest.mark.parametrize("password", [b"some_fancy_bytes", 123])
def test_password_is_required_to_be_a_str(temp_filename, hostname, username, password):
    container = AuthContainer(logging.DEBUG, temp_filename)

    with pytest.raises(TypeError):
        container.add_credentials(hostname, username, password)
