#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Uyuni API integration
"""

from __future__ import absolute_import

import logging
import random
import re
import time
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


@pytest.fixture
def user_name(config):
    """
    Return username from configuration
    """
    return config["valid_objects"]["user"]["name"]


@pytest.fixture
def host_owner(config):
    """
    Return system owner from configuration
    """
    return config["valid_objects"]["hostparams"]["katprep_owner"]


def task_completed(task):
    """
    Returns whether a task is completed
    """
    try:
        if task["successful_count"] > 0:
            return True
        if task["failed_count"] > 0:
            return True
    except KeyError:
        pass
    return False


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
        client.get_host_params("simone.giertz.loc")


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
    assert host_patches


def test_get_host_patches_invalid_format(client):
    """
    Ensure that invalid formats will be discovered
    """
    with pytest.raises(EmptySetException):
        client.get_host_patches("drageekeksi.monitoringlove.local")


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
    assert host_upgrades


def test_get_host_upgrades_invalid_format(client):
    """
    Ensure that invalid formats will be discovered
    """
    with pytest.raises(EmptySetException):
        client.get_host_upgrades("ssibio-13.3-7.noarch")


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
        client.get_host_groups("shittyrobots")


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
        client.get_host_details("sibio.tannenbusch.mitte")


def test_get_host_details_nonexistent(client):
    """
    Ensure that details for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_details(random.randint(800, 1500))


def test_get_host_network(client, host_id):
    """
    Ensure that host network information can be found
    """
    host_network = client.get_host_network(
        host_id
    )
    # check some keys
    keys = [
        "ip",
        "ip6",
        "hostname"
    ]
    for key in keys:
        assert key in host_network.keys()


def test_get_host_network_nonexistent(client):
    """
    Ensure that network information for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_network(random.randint(800, 1500))


def test_get_host_actions(client, host_id):
    """
    Ensure that host actions can be found
    """
    assert client.get_host_actions(
        host_id
    )


def test_get_host_actions_invalid_format(client):
    """
    Ensure that invalid formats will be discovered
    """
    with pytest.raises(EmptySetException):
        client.get_host_actions("t1000.cyberdyne.sys")


def test_get_host_actions_nonexistent(client):
    """
    Ensure that actions for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_actions(random.randint(800, 1500))


def test_host_patch_do_install(client, host_id):
    """
    Ensure that patches can be installed
    """
    # get available patches
    patches = client.get_host_patches(
        host_id
    )
    if patches:
        # install random patch
        _patches = [x["id"] for x in patches]
        action_id = client.install_patches(
            host_id,
            [random.choice(_patches)]
        )
        # wait until task finished before continuing
        while not task_completed(
                client.get_host_action(host_id, action_id[0])[0]
        ):
            # task not finished
            time.sleep(10)
    else:
        raise EmptySetException("No patches available - reset uyuniclient VM")


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
    actions = client.get_host_actions(
        host_id
    )
    _actions = [x["name"] for x in actions if "patch update: opensuse" in x["name"].lower() and x["successful_count"] == 1]     # noqa: E501
    pattern = r'openSUSE-[0-9]{1,4}-[0-9]{1,}'
    errata = [re.search(pattern, x)[0] for x in _actions]
    if errata:
        # find errata ID by patch CVE
        _errata = [client.get_patch_by_name(x)["id"] for x in errata]

        # try to install patch
        with pytest.raises(EmptySetException):
            client.install_patches(
                host_id,
                _errata
            )
    else:
        raise EmptySetException(
            "No patches installed - install patch and rerun test"
        )


def test_host_upgrade_do_install(client, host_id):
    """
    Ensure that package upgrades can be installed
    """
    # get available upgrades
    upgrades = client.get_host_upgrades(
        host_id
    )
    if upgrades:
        # install random upgrade
        _upgrades = [x["to_package_id"] for x in upgrades]
        # install upgrade
        action_id = client.install_upgrades(
            host_id,
            [random.choice(_upgrades)]
        )
        assert isinstance(action_id[0], int)
        # wait until task finished before continuing
        while not task_completed(
                client.get_host_action(host_id, action_id[0])[0]
        ):
            # task not finished
            time.sleep(10)
    else:
        raise EmptySetException("No upgrades available - reset uyuniclient VM")


def test_host_upgrade_invalid_format(client, host_id):
    """
    Ensure that upgrades cannot be installed when supplying
    invalid formats (strings instead of integers)
    """
    with pytest.raises(EmptySetException):
        client.install_upgrades(
            host_id,
            ["csgo-0.8-15", "doge-12.3-4"]
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
            "pinkepank.giertz.loc"
        )


def test_host_reboot_nonexistent(client):
    """
    Ensure that non-existing hosts can't be rebooted
    """
    with pytest.raises(EmptySetException):
        client.host_reboot(
            random.randint(64000, 128000)
        )


def test_get_host_action(client, host_id):
    """
    Ensure that reading information about a
    particular host action is possible
    """
    # select random action
    actions = client.get_host_actions(
        host_id
    )
    action = random.choice(actions)
    # get action details
    details = client.get_host_action(
        host_id, action['id']
    )
    assert details


def test_get_host_action_invalid_format(client, host_id):
    """
    Ensure that reading information about a particular
    host action is not possible when supplying invalid formats
    """
    with pytest.raises(EmptySetException):
        client.get_host_action(
            host_id, "uffgabe0815"
        )


def test_get_host_action_nonexistent(client, host_id):
    """
    Ensure that reading information about
    non-existent host actions is not possible
    """
    with pytest.raises(EmptySetException):
        client.get_host_action(
            host_id, random.randint(1337, 6667)
        )


def test_get_user(client, user_name):
    """
    Ensure that user information can be found
    """
    user_info = client.get_user(
        user_name
    )
    # check some keys
    keys = [
        "first_name",
        "last_name",
        "email",
        "org_id",
        "org_name"
    ]
    for key in keys:
        assert key in user_info.keys()


def test_get_user_nonexistent(client):
    """
    Ensure that user information for invalid users cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_user("hidethepain %s" % random.randint(800, 1500))


def test_get_host_owner(client, host_id, host_owner):
    """
    Ensure that host owner information can be found
    """
    _owner = client.get_host_owner(host_id)
    assert _owner == host_owner


def test_get_host_owner_nonexistent(client):
    """
    Ensure that host owner information for invalid machines cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_owner(random.randint(800, 1500))
