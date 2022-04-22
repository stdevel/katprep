"""
Unit tests for Uyuni API integration
"""

import logging
import random
import re
import time
from datetime import datetime
import pytest
from katprep.host import Host
from katprep.management.uyuni import UyuniAPIClient
from katprep.exceptions import (
    EmptySetException,
    InvalidCredentialsException,
    SessionException,
    SSLCertVerificationError,
    CustomVariableExistsException
)

from .utilities import load_config


@pytest.fixture(scope='session')
def config():
    """
    Load test configuration
    """
    return load_config("uyuni_config.json")


@pytest.fixture(scope='session')
def client(config):
    """
    Instance client
    """
    return UyuniAPIClient(
        logging.ERROR,
        config["config"]["hostname"],
        config["config"]["api_user"],
        config["config"]["api_pass"],
        port=config["config"]["port"],
        verify=False
    )


@pytest.fixture
def host_obj(client, config):
    """
    Returns a host object
    """
    system_id = config["valid_objects"]["host"]["id"]
    _host = Host(
        config["valid_objects"]["host"]["name"],
        client.get_host_params(system_id),
        client.get_organization(),
        location=client.get_location(),
        verifications=None,
        patches=client.get_host_patches(system_id),
        management_id=system_id
    )
    return _host

@pytest.fixture
def incorrect_host_obj():
    """
    Returns an incorrect host object
    """
    system_id = random.randint(800, 1500)
    _host = Host(
        f"duck{random.randint(800, 1500)}",
        system_id,
        "Duckburg",
        "Duckburg",
        verifications=None,
        patches={},
        management_id=system_id
    )
    return _host

@pytest.fixture
def host_id(config):
    """
    Return host ID from configuration
    """
    return config["valid_objects"]["host"]["id"]

@pytest.fixture
def host_name(config):
    """
    Return hostname from configuration
    """
    return config["valid_objects"]["host"]["name"]

@pytest.fixture
def hostgroup_name(config):
    """
    Return hostgroup name from configuration
    """
    return config["valid_objects"]["hostgroup"]["name"]

@pytest.fixture
def hostparams(config):
    """
    Return host parameters
    """
    return config["valid_objects"]["hostparams"]

@pytest.fixture
def customvars(config):
    """
    Return custom info keys
    """
    return config["valid_objects"]["customvars"]

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
        config["config"]["hostname"],
        config["config"]["api_user"],
        config["config"]["api_pass"],
        port=config["config"]["port"],
        verify=False
    )


def test_invalid_login(config):
    """
    Ensure exceptions on invalid logins
    """
    with pytest.raises(InvalidCredentialsException):
        UyuniAPIClient(
            logging.ERROR,
            config["config"]["hostname"],
            "giertz",
            "paulapinkepank",
            port=config["config"]["port"],
            verify=False
        )


def test_invalid_ssl(config):
    """
    Ensure that invalid SSL certs crash the client
    """
    with pytest.raises(SSLCertVerificationError):
        UyuniAPIClient(
            logging.ERROR,
            config["config"]["hostname"],
            config["config"]["api_user"],
            config["config"]["api_pass"],
            port=config["config"]["port"],
            verify=True
        )


def test_get_hosts(client):
    """
    Ensure that all host IDs can be listed
    """
    for host in client.get_hosts():
        # we only deal with integers
        assert isinstance(host, int)


def test_get_hosts_by_hostgroup(client, hostgroup_name):
    """
    Ensure that hosts can be found by hostgroup names
    """
    for host in client.get_hosts_by_hostgroup(hostgroup_name):
        # we only deal with integers
        assert isinstance(host, int)


def test_get_hosts_by_hostgroup_nonexistent(client):
    """
    Ensure that hosts cannot be found by invalides hostgroups
    """
    with pytest.raises(EmptySetException):
        client.get_hosts_by_hostgroup("SLE%s" % random.randint(8, 16))


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


def test_get_hostname_by_id(client, host_id, host_name):
    """
    Ensure that hostname can retrieved by ID
    """
    system_name = client.get_hostname_by_id(
        host_id
    )
    assert system_name == host_name


def test_get_hostname_by_id_nonexistent(client):
    """
    Ensure that hostname cannot retrieved by invalid ID
    """
    with pytest.raises(EmptySetException):
        client.get_hostname_by_id(random.randint(800, 1500))


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
    if not host_upgrades:
        raise EmptySetException("No upgrades available - reset uyuniclient VM")
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


@pytest.mark.parametrize("key", [
    "id",
    "profile_name",
    "hostname",
    "virtualization"
])
def test_get_host_details(client, host_id, key):
    """
    Ensure that host details can be found
    """
    host_details = client.get_host_details(
        host_id
    )
    # check some keys
    assert key in host_details


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


@pytest.mark.parametrize("key", [
    "ip",
    "ip6",
    "hostname"
])
def test_get_host_network(client, host_id, key):
    """
    Ensure that host network information can be found
    """
    host_network = client.get_host_network(
        host_id
    )
    # check some keys
    assert key in host_network


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


def test_host_patch_do_install(client, host_obj):
    """
    Ensure that patches can be installed
    """
    # get available patches
    if not host_obj.patches:
        raise EmptySetException("No patches available - reset uyuniclient VM")

    # install random patch
    _patches = [x["id"] for x in host_obj.patches]
    action_id = client.install_patches(
        host_obj,
        [random.choice(_patches)]
    )
    # wait until task finished before continuing
    action_id = action_id[0]
    task = client.get_host_action(host_obj.management_id, action_id)[0]
    while not task_completed(task):
        time.sleep(10)
        task = client.get_host_action(host_obj.management_id, action_id)[0]


def test_host_patch_invalid_format(client, host_obj):
    """
    Ensure that patches cannot be installed when supplying
    invalid formats (strings instead of integers)
    """
    with pytest.raises(EmptySetException):
        client.install_patches(
            host_obj,
            ["BA-libpinkepank", "gcc-13.37"]
        )


def test_host_patch_nonexistent(client, host_obj):
    """
    Ensure that non-existing patches cannot be installed
    """
    with pytest.raises(EmptySetException):
        client.install_patches(
            host_obj,
            [random.randint(64000, 128000)]
        )


def test_host_patch_already_installed(client, host_obj):
    """
    Ensure that already installed patches cannot be installed
    """
    # find already installed errata by searching actions
    actions = client.get_host_actions(
        host_obj.management_id
    )
    today = datetime.now().strftime("%Y-%m-%d")
    _actions = [x["name"] for x in actions if x['action_type'] == 'Patch Update' and today in x["earliest_action"] and x["successful_count"] == 1]     # pylint: disable=line-too-long # noqa: E501
    # search for SUSE errata pattern
    errata = []
    pattern = r'openSUSE-?(SLE-15.[1-5]{1}-)[0-9]{1,4}-[0-9]{1,}'
    for _act in _actions:
        try:
            errata.append(re.search(pattern, _act)[0])
        except TypeError:
            pass

    # abort if no patches found
    if not errata:
        raise EmptySetException(
            "No patches installed - install patch and rerun test"
        )

    # get installed errata IDs
    _errata = [client.get_patch_by_name(x)["id"] for x in errata]
    # try to install random patch
    with pytest.raises(EmptySetException):
        client.install_patches(
            host_obj,
            [random.choice(_errata)]
        )


def test_host_upgrade_do_install(client, host_obj):
    """
    Ensure that package upgrades can be installed
    """
    # get available upgrades
    upgrades = client.get_host_upgrades(
        host_obj.management_id
    )
    if not upgrades:
        raise EmptySetException("No upgrades available - reset uyuniclient VM")

    # install random upgrade
    _upgrades = [x["to_package_id"] for x in upgrades]
    # install upgrade
    action_id = client.install_upgrades(
        host_obj,
        [random.choice(_upgrades)]
    )
    assert isinstance(action_id[0], int)
    # wait until task finished before continuing
    action_id = action_id[0]
    task = client.get_host_action(host_obj.management_id, action_id)[0]
    while not task_completed(task):
        time.sleep(10)
        task = client.get_host_action(host_obj.management_id, action_id)[0]


def test_host_upgrade_invalid_format(client, host_obj):
    """
    Ensure that upgrades cannot be installed when supplying
    invalid formats (strings instead of integers)
    """
    with pytest.raises(EmptySetException):
        client.install_upgrades(
            host_obj,
            ["csgo-0.8-15", "doge-12.3-4"]
        )


def test_host_upgrade_nonexistent(client, host_obj):
    """
    Ensure that non-existing upgrades cannot be installed
    """
    with pytest.raises(EmptySetException):
        client.install_upgrades(
            host_obj,
            [random.randint(64000, 128000)]
        )


def test_reboot_host(client, host_obj):
    """
    Ensures that hosts can be rebooted
    """
    action_id = client.reboot_host(
        host_obj
    )
    assert isinstance(action_id, int)


def test_reboot_host_invalid(client, incorrect_host_obj):
    """
    Ensure that invalid hosts can't be rebooted
    """
    with pytest.raises(EmptySetException):
        client.reboot_host(
            incorrect_host_obj
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


@pytest.mark.parametrize("key", [
    "first_name",
    "last_name",
    "email",
    "org_id",
    "org_name"
])
def test_get_user(client, user_name, key):
    """
    Ensure that user information can be found
    """
    user_info = client.get_user(
        user_name
    )
    # check some keys
    assert key in user_info


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


def test_get_host_custom_variables(client, host_id, hostparams):
    """
    Ensure that host custom values can be found
    """
    _variables = client.get_host_custom_variables(host_id)
    for _param in hostparams:
        assert _param in _variables.keys()
        assert hostparams[_param] == _variables[_param]


def test_get_host_custom_variables_nonexistent(client):
    """
    Ensure that host custom values for invalid machines cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_custom_variables(random.randint(800, 1500))


def test_errata_task_status(client, host_id):
    """
    Ensure that errata installation task status can be gathered
    """
    # TODO: ensure that at least one errata was installed previously
    # pick random errata task
    actions = client.get_errata_task_status(host_id)
    action = random.choice(actions)
    # get action details
    details = client.get_host_action(
        host_id, action['id']
    )
    assert details


def test_errata_task_status_nonexistent(client):
    """
    Ensure that errata task information for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_errata_task_status(
            random.randint(800, 1500)
        )


def test_upgrade_task_status(client, host_id):
    """
    Ensure that package upgrade task status can be gathered
    """
    # TODO: ensure that at least one update was installed previously
    # pick random errata task
    actions = client.get_upgrade_task_status(host_id)
    action = random.choice(actions)
    # get action details
    details = client.get_host_action(
        host_id, action['id']
    )
    assert details


def test_upgrade_task_status_nonexistent(client):
    """
    Ensure that upgrade task information for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_upgrade_task_status(
            random.randint(800, 1500)
        )


def test_script_task_status(client, host_id):
    """
    Ensure that script execution task status can be gathered
    """
    # pick random script task
    actions = client.get_script_task_status(host_id)
    action = random.choice(actions)
    # get action details
    details = client.get_host_action(
        host_id, action['id']
    )
    assert details


def test_script_task_status_nonexistent(client):
    """
    Ensure that script task information for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_script_task_status(
            random.randint(800, 1500)
        )


def test_get_custom_variables(client, customvars):
    """
    Ensure that custom variables can be found
    """
    _variables = client.get_custom_variables()
    for _param in customvars:
        assert _param in _variables.keys()
        assert customvars[_param] == _variables[_param]


def test_create_update_delete_custom_variable(client):
    """
    Ensure that custom variables can be added, updated and deleted
    """
    _variables = {
        "katprep_maintainer": "Defines the maintainerz",
        "katprep_update_channel": "Defines the update chanel"
    }
    _changed_variables = {
        "katprep_maintainer": "Defines the maintainer",
        "katprep_update_channel": "Defines the update channel"
    }

    # create variables
    for _var in _variables:
        client.create_custom_variable(_var, _variables[_var])
    # update variables
    for _var in _changed_variables:
        client.update_custom_variable(_var, _changed_variables[_var])
    # delete variables
    for _var in _variables:
        client.delete_custom_variable(_var)


def test_create_custom_variable_already_existing(client, customvars):
    """
    Ensure that already existing custom variables can't be re-created
    """
    with pytest.raises(CustomVariableExistsException):
        for _var in customvars:
            client.create_custom_variable(_var, customvars[_var])


def test_update_custom_variable_nonexisting(client):
    """
    Ensure that updating a non-existing custom variable isn't possible
    """
    with pytest.raises(EmptySetException):
        client.update_custom_variable(
            random.randint(800, 1500), random.randint(800, 1500)
        )


def test_delete_custom_variable_nonexisting(client):
    """
    Ensure that removing a non-existing custom variable isn't possible
    """
    with pytest.raises(EmptySetException):
        client.delete_custom_variable(
            random.randint(800, 1500)
        )


def test_set_update_delete_host_custom_variables(client, host_id):
    """
    Ensure that host custom values can be set and updated
    """
    _variables = {
        "katprep_pre-script": "sleep 60",
        "katprep_post-script": "sleep 30"
    }
    for _var in _variables:
        # set custom variable
        client.host_add_custom_variable(
            host_id, _var, _variables[_var]
        )
        # update custom variable
        client.host_update_custom_variable(
            host_id, _var, "DietmarDiamantUltras"
        )
        # delete custom variable
        client.host_delete_custom_variable(
            host_id, _var
        )


def test_set_host_custom_variables_nonexisting(client, host_id):
    """
    Ensure that non-existing custom values can't be set for a host
    """
    with pytest.raises(EmptySetException):
        client.host_add_custom_variable(
            host_id, "katprep_motd", "Heer mir uff"
        )


def test_delete_host_custom_variables_nonexisting(client, host_id):
    """
    Ensure that non-existing custom values can't be deleted from a host
    """
    with pytest.raises(EmptySetException):
        client.host_add_custom_variable(
            host_id, "katprep_motd", "HurraHurraWirSchiffeUebernMaa"
        )

def test_run_host_command(client, host_id):
    """
    Ensure that commands can be run on hosts
    """
    _cmds = [
        """#!/bin/sh
uptime""",
        "uptime"
    ]
    for _cmd in _cmds:
        result = client.host_run_command(host_id, _cmd)
        assert isinstance(result, int)


def test_run_host_command_nonexistent(client):
    """
    Ensure that commands can't be executed on non-existing hosts
    """
    with pytest.raises(EmptySetException):
        client.host_run_command(
            random.randint(800, 1500),
            "uptime"
        )


def test_get_actionchains(client):
    """
    Ensure that action chains can be retrieved
    """
    two_chainz = client.get_actionchains()
    assert isinstance(two_chainz, list)


def test_create_add_list_run_actionchains(client, host_id):
    """
    Ensure that action chains can be managed
    """
    # get host patches and package upgrades
    patches = client.get_host_patches(host_id)
    _patches = [x["id"] for x in patches]
    upgrades = client.get_host_upgrades(host_id)
    _upgrades = [x["to_package_id"] for x in upgrades]

    if not upgrades:
        raise EmptySetException("No upgrades available - reset uyuniclient VM")
    if not patches:
        raise EmptySetException("No patches available - reset uyuniclient VM")

    # create action chain
    chain_label = f"{host_id}_{random.randint(800, 1500)}"
    chain_id = client.add_actionchain(chain_label)

    # add patch update
    client.actionchain_add_patches(
        chain_label,
        host_id,
        [random.choice(_patches)]
    )

    # add package upgrade
    client.actionchain_add_upgrades(
        chain_label,
        host_id,
        [random.choice(_upgrades)]
    )

    # add remote command
    client.actionchain_add_command(
        chain_label,
        host_id,
        "sleep 10"
    )

    # list actions
    actions = client.get_actionchain_actions(chain_label)
    # ensure that 3 actions are defined
    assert len(actions) == 3

    # run action chain
    action_id = client.run_actionchain(chain_label)
    # ensure that an action ID is retrieved
    assert isinstance(action_id, int)


def test_create_actionchain_incorrect(client):
    """
    Ensure that action chains without labels can't be created
    """
    with pytest.raises(EmptySetException):
        client.add_actionchain("")


def test_run_actionchain_nonexisting(client):
    """
    Ensure that non-existing action chains can be scheduled
    """
    with pytest.raises(EmptySetException):
        client.run_actionchain(random.randint(800, 1500))


def test_delete_actionchain_nonexisting(client):
    """
    Ensure that non-existing action chains can't be deleted
    """
    with pytest.raises(EmptySetException):
        client.delete_actionchain(random.randint(800, 1500))


def test_nonexisting_actionchain_add_patches(client, host_id):
    """
    Ensure that patches can't be added to non-existing action chains
    """
    with pytest.raises(EmptySetException):
        client.actionchain_add_patches(
            random.randint(800, 1500),
            host_id,
            [random.randint(800, 1500)]
        )


def test_actionchain_add_patches_nonexisting(client, host_id):
    """
    Ensure that non-existing patches can't be used
    """
    # try adding non-existing patches action chain
    chain_label = f"{host_id}_{random.randint(800, 1500)}"
    client.add_actionchain(chain_label)
    with pytest.raises(EmptySetException):
        client.actionchain_add_patches(
            chain_label, host_id, [random.randint(8000, 15000)]
        )

    # cleanup
    client.delete_actionchain(chain_label)


def test_nonexisting_actionchain_add_upgrades(client, host_id):
    """
    Ensure that upgrades can't be added to non-existing action chains
    """
    with pytest.raises(EmptySetException):
        client.actionchain_add_upgrades(
            random.randint(800, 1500),
            host_id,
            [random.randint(800, 1500)]
        )


def test_actionchain_add_upgrades_nonexisting(client, host_id):
    """
    Ensure that non-existing upgrades can't be used
    """
    # try adding non-existing upgrades action chain
    chain_label = f"{host_id}_{random.randint(800, 1500)}"
    client.add_actionchain(chain_label)
    with pytest.raises(EmptySetException):
        client.actionchain_add_upgrades(
            chain_label, host_id, [random.randint(80000, 150000)]
        )

    # cleanup
    client.delete_actionchain(chain_label)


def test_nonexisting_actionchain_add_command(client, host_id):
    """
    Ensure that commands can't be added to non-existing action chains
    """
    with pytest.raises(EmptySetException):
        client.actionchain_add_command(
            random.randint(800, 1500),
            host_id,
            "sleep 10"
        )


def test_actionchain_add_nonexisting_command(client, host_id):
    """
    Ensure that empty commands can't be added to action chains
    """
    # try adding non-existing upgrades action chain
    chain_label = f"{host_id}_{random.randint(800, 1500)}"
    client.add_actionchain(chain_label)
    with pytest.raises(EmptySetException):
        client.actionchain_add_command(
            chain_label, host_id, ""
        )

    # cleanup
    client.delete_actionchain(chain_label)


def test_host_upgrade_scripts(host_obj, client):
    """
    Set pre/post scripts and run maintenance
    """
    # get available upgrades
    upgrades = client.get_host_upgrades(
        host_obj.management_id
    )
    if not upgrades:
        raise EmptySetException("No upgrades available - reset uyuniclient VM")

    # set custom variables
    _vars = {
        "katprep_pre-script": "sleep 10",
        "katprep_post-script": "sleep 10"
    }
    for _var in _vars:
        client.host_add_custom_variable(
            host_obj.management_id,
            _var, _vars[_var]
        )
        host_obj._params[_var] = _vars[_var]

    # install random upgrade
    _upgrades = [x["to_package_id"] for x in upgrades]
    # install upgrade
    _action_ids = client.install_upgrades(
        host_obj,
        [random.choice(_upgrades)]
    )

    # check for tasks
    _actions = [x['id'] for x in client.get_host_actions(host_obj.management_id)]
    for _act in _action_ids:
        assert _act in _actions

    # remove custom variables
    for _var in _vars:
        client.host_delete_custom_variable(
            host_obj.management_id,
            _var
        )


def test_host_patch_scripts(host_obj, client):
    """
    Set pre/post scripts and run maintenance
    """
    # get available patches
    patches = client.get_host_patches(
        host_obj.management_id
    )
    if not patches:
        raise EmptySetException("No patches available - reset uyuniclient VM")

    # set custom variables
    _vars = {
        "katprep_pre-script": "sleep 10",
        "katprep_post-script": "sleep 10"
    }
    for _var in _vars:
        client.host_add_custom_variable(
            host_obj.management_id,
            _var, _vars[_var]
        )
        host_obj._params[_var] = _vars[_var]

    # install random patch
    _patches = [x["id"] for x in patches]
    # install upgrade
    _action_ids = client.install_patches(
        host_obj,
        [random.choice(_patches)]
    )

    # check for tasks
    _actions = [x['id'] for x in client.get_host_actions(host_obj.management_id)]
    for _act in _action_ids:
        assert _act in _actions

    # remove custom variables
    for _var in _vars:
        client.host_delete_custom_variable(
            host_obj.management_id,
            _var
        )
