import logging
import os
import os.path
from collections import namedtuple

import pytest
from katprep.AuthContainer import AuthContainer, ContainerException

Py2File = namedtuple("Py2File", ["filename", "key"])


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


@pytest.fixture(params=["hall0w3lt!", None], ids=["encrypted", "unencrypted"])
def encryption_key(request):
    yield request.param


@pytest.fixture
def container(encryption_key, temp_filename):
    if encryption_key:
        cont = AuthContainer(logging.DEBUG, temp_filename, encryption_key)
    else:
        cont = AuthContainer(logging.DEBUG, temp_filename)

    yield cont


def test_reading_from_file(
    container, encryption_key, temp_filename, hostname, username, password
):
    container.add_credentials(hostname, username, password)
    container.save()

    if encryption_key:
        new_container = AuthContainer(logging.DEBUG, temp_filename, encryption_key)
    else:
        new_container = AuthContainer(logging.DEBUG, temp_filename)

    creds = new_container.get_credential(hostname)
    assert creds.username == username
    assert creds.password == password


def test_listing_hostnames(container, hostname, username, password):
    assert not container.get_hostnames()
    container.add_credentials(hostname, username, password)

    assert [hostname] == container.get_hostnames()


def test_retrieving_unknown_credential(container, hostname, username, password):
    container.add_credentials(hostname, username, password)

    assert None == container.get_credential("nothere" + hostname)


def test_not_setting_empty_key(container):
    if container.is_encrypted():
        pytest.skip("Requiring unencrypted container")

    assert not container.is_encrypted()
    container.set_key("")
    assert not container.is_encrypted()


def test_setting_key(container):
    if container.is_encrypted():
        pytest.skip("Requiring unencrypted container")

    container.set_key("sosecret")
    assert container.is_encrypted()


def test_removing_credential(container, hostname, username, password):
    assert None == container.get_credential(hostname)

    container.add_credentials(hostname, username, password)
    assert container.get_credential(hostname)

    container.remove_credentials(hostname)
    assert None == container.get_credential(hostname)


@pytest.fixture(
    params=[
        ("container-py2-unencrypted.auth", None),
        ("container-py2.auth", "test123"),
    ],
    ids=["unencrypted", "encrypted"],
)
def python_2_files(request):
    test_dir = os.path.dirname(os.path.abspath(__file__))

    filepath = os.path.join(test_dir, request.param[0])
    encryption_key = request.param[1]

    yield Py2File(filepath, encryption_key)


@pytest.fixture
def py2container(python_2_files):
    filename = python_2_files.filename
    key = python_2_files.key

    if key:
        container = AuthContainer(logging.DEBUG, filename, key)
    else:
        container = AuthContainer(logging.DEBUG, filename)

    yield container


def test_importing_python_2_file(py2container):
    container = py2container

    hostnames = container.get_hostnames()
    assert 1 == len(hostnames)

    creds = container.get_credential(hostnames[0])
    assert creds.username == "username"
    assert creds.password == "password"


def test_import_encrypted_python_2_file_with_wrong_keyword(py2container):
    container = py2container
    container.set_key("invalidkey")

    hostnames = container.get_hostnames()
    assert len(hostnames) >= 1

    with pytest.raises(ContainerException):
        container.get_credential(hostnames[0])


@pytest.mark.parametrize("password", [b"some_fancy_bytes", 123])
def test_password_is_required_to_be_a_str(container, hostname, username, password):
    with pytest.raises(TypeError):
        container.add_credentials(hostname, username, password)


def test_deleting_missing_hostname_does_not_fail(container, hostname):
    assert not container.get_hostnames()
    container.remove_credentials(hostname)
