#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Uyuni API integration
"""

from __future__ import absolute_import

import logging
import random
import re
import pytest
from katprep.management.uyuni import UyuniAPIClient
from katprep.exceptions import (
    SSLCertVerificationError,
    SessionException,
    EmptySetException,
    InvalidCredentialsException
)

from .utilities import load_config


@pytest.fixture(scope='session')
def config():
    """
    Load test configuration
    """
    return load_config("uyuni_config.json")


@pytest.fixture
def client(config):
    """
    Instance client
    """
    return UyuniAPIClient(
        logging.ERROR,
        config["config"]["api_user"],
        config["config"]["api_pass"],
        config["config"]["hostname"],
        port=config["config"]["port"],
        skip_ssl=True
    )


@pytest.fixture
def host_id(config):
    """
    Return host ID from configuration
    """
    return config["valid_objects"]["host"]["id"]


def test_valid_login(config):
    """
    Ensure valid logins are possible
    """
    assert UyuniAPIClient(
        logging.ERROR,
        config["config"]["api_user"],
        config["config"]["api_pass"],
        config["config"]["hostname"],
        port=config["config"]["port"],
        skip_ssl=True
    )


def test_invalid_login(config):
    """
    Ensure exceptions on invalid logins
    """
    with pytest.raises(InvalidCredentialsException):
        UyuniAPIClient(
            logging.ERROR,
            "giertz",
            "paulapinkepank",
            config["config"]["hostname"],
            port=config["config"]["port"],
            skip_ssl=True
        )


def test_invalid_ssl(config):
    """
    Ensure that invalid SSL certs crash the client
    """
    with pytest.raises(SSLCertVerificationError):
        UyuniAPIClient(
            logging.ERROR,
            config["config"]["api_user"],
            config["config"]["api_pass"],
            config["config"]["hostname"],
            port=config["config"]["port"],
            skip_ssl=False
        )


def test_get_hosts(client):
    """
    Ensure that all hosts can be listed
    """
    for host in client.get_hosts():
        # we only deal with integers
        assert isinstance(host, int)


def test_get_host_id(client, config, host_id):
    """
    Ensure that host ID can retrieved by name
    """
    system_id = client.get_host_id(
        config["valid_objects"]["host"]["name"]
    )
    assert system_id == host_id


def test_get_host_id_nonexistent(client):
    """
    Ensure that host ID cannot retrieved by invalid name
    """
    with pytest.raises(EmptySetException):
        client.get_host_id("web%s" % random.randint(800, 1500))


def test_get_host_params(client, config, host_id):
    """
    Ensure that host params can be retrieved
    """
    host_params = client.get_host_params(
        host_id
    )
    for key, value in config["valid_objects"]["hostparams"].items():
        assert host_params[key] == value


def test_get_host_params_invalid_format(client):
    """
    Ensure that host params cannot be retrieved by supplying invalid format
    """
    with pytest.raises(EmptySetException):
        client.get_host_params("web1337")


def test_get_host_params_nonexistent(client):
    """
    Ensure that host params cannot be retrieved by supplying invalid IDs
    """
    with pytest.raises(SessionException):
        client.get_host_params(random.randint(800, 1500))


def test_get_host_patches(client, host_id):
    """
    Ensure that host patches can be found
    """
    host_patches = client.get_host_patches(
        host_id
    )
    assert len(host_patches) > 0


def test_get_host_patches_invalid_format(client):
    """
    Ensure that invalid formats will be discovered
    """
    with pytest.raises(EmptySetException):
        client.get_host_patches("web1337")


def test_get_host_patches_nonexistent(client):
    """
    Ensure that patches for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_patches(random.randint(800, 1500))


def test_get_host_upgrades(client, host_id):
    """
    Ensure that host package upgrades can be found
    """
    host_upgrades = client.get_host_upgrades(
        host_id
    )
    assert len(host_upgrades) > 0


def test_get_host_upgrades_invalid_format(client):
    """
    Ensure that invalid formats will be discovered
    """
    with pytest.raises(EmptySetException):
        client.get_host_upgrades("web1337")


def test_get_host_upgrades_nonexistent(client):
    """
    Ensure that package upgrades for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_upgrades(random.randint(800, 1500))


def test_get_host_groups(client, config, host_id):
    """
    Ensure that host groups can be found
    """
    host_groups = client.get_host_groups(
        host_id
    )
    _groups = [x['system_group_name'] for x in host_groups]
    assert config["valid_objects"]["host"]["group"] in _groups


def test_get_host_groups_invalid_format(client):
    """
    Ensure that invalid formats will be discovered
    """
    with pytest.raises(EmptySetException):
        client.get_host_groups("web1337")


def test_get_host_groups_nonexistent(client):
    """
    Ensure that host groups for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_groups(random.randint(800, 1500))


def test_get_host_details(client, host_id):
    """
    Ensure that host details can be found
    """
    host_details = client.get_host_details(
        host_id
    )
    # check some keys
    keys = [
        "id",
        "profile_name",
        "hostname",
        "virtualization"
    ]
    for key in keys:
        assert key in host_details.keys()


def test_get_host_details_invalid_format(client):
    """
    Ensure that invalid formats will be discovered
    """
    with pytest.raises(EmptySetException):
        client.get_host_details("web1337")


def test_get_host_details_nonexistent(client):
    """
    Ensure that details for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_details(random.randint(800, 1500))


def test_get_host_tasks(client, host_id):
    """
    Ensure that host tasks can be found
    """
    host_tasks = client.get_host_tasks(
        host_id
    )
    keys = [
        "name",
        "id",
        "pickup_time",
        "completion_time",
        "result_msg"
    ]
    for task in host_tasks:
        for key in keys:
            assert key in task.keys()


def test_get_host_tasks_invalid_format(client):
    """
    Ensure that invalid formats will be discovered
    """
    with pytest.raises(EmptySetException):
        client.get_host_tasks("web1337")


def test_get_host_tasks_nonexistent(client):
    """
    Ensure that tasks for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_tasks(random.randint(800, 1500))


def test_host_patch_do_install(client, host_id):
    """
    Ensure that patches can be installed
    """
    # get available patches
    patches = client.get_host_patches(
        host_id
    )
    # install random patch
    _patches = [x["id"] for x in patches]
    action_id = client.install_patches(
        host_id,
        [random.choice(_patches)]
    )
    assert isinstance(action_id[0], int)
    # TODO: wait to allow later tests to succeed?


def test_host_patch_invalid_format(client, host_id):
    """
    Ensure that patches cannot be installed when supplying
    invalid formats (strings instead of integers)
    """
    with pytest.raises(EmptySetException):
        client.install_patches(
            host_id,
            ["BA-libpinkepank", "gcc-13.37"]
        )


def test_host_patch_nonexistent(client, host_id):
    """
    Ensure that non-existing patches cannot be installed
    """
    with pytest.raises(EmptySetException):
        client.install_patches(
            host_id,
            [random.randint(64000, 128000)]
        )


def test_host_patch_already_installed(client, host_id):
    """
    Ensure that already installed patches cannot be installed
    """
    # find already installed errata by searching actions
    actions = client.get_host_tasks(
        host_id
    )
    _actions = [x["name"] for x in actions if "patch update: opensuse" in x["name"].lower() and x["successful_count"] == 1]     # noqa: E501
    pattern = r'openSUSE-[0-9]{1,4}-[0-9]{1,}'
    errata = [re.search(pattern, x)[0] for x in _actions]
    # find errata ID by patch CVE
    _errata = [client.get_patch_by_name(x)["id"] for x in errata]

    # try to install patch
    with pytest.raises(EmptySetException):
        client.install_patches(
            host_id,
            _errata
        )


def test_host_upgrade_do_install(client, host_id):
    """
    Ensure that package upgrades can be installed
    """
    # get available upgrades
    upgrades = client.get_host_upgrades(
        host_id
    )
    # install random upgrade
    _upgrades = [x["to_package_id"] for x in upgrades]
    # install upgrade
    action_id = client.install_upgrades(
        host_id,
        [random.choice(_upgrades)]
    )
    assert isinstance(action_id, int)
    # TODO: wait to allow later tests to succeed?


def test_host_upgrade_invalid_format(client, host_id):
    """
    Ensure that upgrades cannot be installed when supplying
    invalid formats (strings instead of integers)
    """
    with pytest.raises(EmptySetException):
        client.install_upgrades(
            host_id,
            ["BA-libpinkepank", "gcc-13.37"]
        )


def test_host_upgrade_nonexistent(client, host_id):
    """
    Ensure that non-existing upgrades cannot be installed
    """
    with pytest.raises(EmptySetException):
        client.install_upgrades(
            host_id,
            [random.randint(64000, 128000)]
        )


def test_host_upgrade_already_installed(client, host_id):
    """
    Ensure that already installed upgrades cannot be installed
    """
    # find already installed errata by searching actions
    actions = client.get_host_tasks(
        host_id
    )
    _packages = [x["additional_info"][0]["detail"] for x in actions if "package install/upgrade" in x["name"].lower() and x["successful_count"] == 1]     # noqa: E501
    print(_packages)
    # pattern = r'openSUSE-[0-9]{1,4}-[0-9]{1,}'
    # errata = [re.search(pattern, x)[0] for x in _actions]
    # find errata ID by patch CVE
    # _errata = [client.get_patch_by_name(x)["id"] for x in errata]

    # try to install patch
    # with pytest.raises(EmptySetException):
    #    client.install_patches(
    #        host_id,
    #        _errata
    #    )
    # TODO: how to check?


def test_host_reboot(client, host_id):
    """
    Ensures that hosts can be rebooted
    """
    action_id = client.host_reboot(
        host_id
    )
    assert isinstance(action_id, int)


def test_host_reboot_invalid_format(client):
    """
    Ensure that hosts with invalid format can't be rebooted
    """
    with pytest.raises(EmptySetException):
        client.host_reboot(
            "pinepank.giertz.loc"
        )


def test_host_reboot_nonexistent(client):
    """
    Ensure that non-existing hosts can't be rebooted
    """
    with pytest.raises(EmptySetException):
        client.host_reboot(
            random.randint(64000, 128000)
        )
