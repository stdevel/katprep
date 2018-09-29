#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Pyvmomi integration
"""
from __future__ import absolute_import

import logging
import pytest
import time
from katprep.clients.PyvmomiClient import PyvmomiClient
from katprep.clients import SessionException, InvalidCredentialsException, \
EmptySetException

from .utilities import load_config


# scope used to reuse the same fixture for all tests
@pytest.fixture(scope="session")
def config():
    return load_config("pyvmomi_config.json")


@pytest.fixture
def client(config):
    try:
        yield PyvmomiClient(
            logging.ERROR,
            config["config"]["hostname"],
            config["config"]["api_user"],
            config["config"]["api_pass"]
        )
    finally:
        # Executes this after every test
        # wait for changes to be applied
        time.sleep(20)


def test_valid_login(config, client, snapshot_name):
    """
    Ensure exceptions on valid logins
    """
    try:
        result = client.has_snapshot(
            config["valid_objects"]["vm"],
            snapshot_name
        )
        assert result in [True, False]
    except EmptySetException:
        # An alternative could be to use a skip here to give a reason
        # why this has been skipped
        # pytest.skip("Insert reason here...")
        pass


def test_invalid_login(config):
    """
    Ensure exceptions on invalid logins
    """
    with pytest.raises(InvalidCredentialsException):
        api_dummy = PyvmomiClient(
            logging.ERROR,
            config["config"]["hostname"],
            "giertz",
            "paulapinkepank"
        )

        api_dummy.get_vm_ips()  # dummy call


def test_a_get_vm_ips(client, config):
    """
    Ensure that receiving VMs with their IPs is possible
    """
    vm_ips = client.get_vm_ips()
    assert config["valid_objects"]["vm"] in vm_ips


def test_a_get_vm_hosts(client, config):
    """
    Ensure that receiving VMs with their hosts is possible
    """
    vm_hosts = client.get_vm_hosts()
    assert config["valid_objects"]["vm"] in vm_hosts


@pytest.mark.parametrize("forcefully", values=[True, False])
def test_restart_vm(client, config, forcefully):
    """
    Ensure that restarting VMs is possible
    """
    client.restart_vm(config["valid_objects"]["vm"], force=forcefully)


@pytest.mark.parametrize("forcefully", values=[True, False])
def test_restart_vm_fail(virtClient, nonexisting_vm, forcefully):
    """
    Ensure that restarting non-existing VMs is not possible
    """
    with pytest.raises(SessionException):
        virtClient.restart_vm(nonexisting_vm, force=forcefully)


def test_get_vm_powerstate(client, config):
    """
    Ensure that retrieving a VM's powerstate is possible
    """
    vm = config["valid_objects"]["vm"]
    assert client.powerstate_vm(vm) in ["poweredOn", "poweredOff"]


def test_get_vm_powerstate_fail(client, nonexisting_vm):
    """
    Ensure that retrieving a non-existent VM's powerstate is not possible
    """
    with pytest.raises(SessionException):
        client.powerstate_vm(nonexisting_vm)


def test_vm_powerchange(client, config):
    """
    Ensure that powering off a VM is possible
    """
    vm = config["valid_objects"]["vm"]
    client.poweroff_vm(vm)
    client.poweron_vm(vm)


def test_vm_poweroff_fail(client, nonexisting_vm):
    """
    Ensure that powering off a non-existing VM is not possible
    """
    with pytest.raises(SessionException):
        client.poweroff_vm(nonexisting_vm)


def test_vm_poweron_fail(client, nonexisting_vm):
    """
    Ensure that powering on a non-existing VM is not possible
    """
    with pytest.raises(SessionException):
        client.poweron_vm(nonexisting_vm)
