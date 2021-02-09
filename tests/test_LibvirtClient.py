#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Libvirt integration
"""

from __future__ import absolute_import, print_function

import logging
import pytest
from katprep.management.exceptions import (EmptySetException,
InvalidCredentialsException, SessionException)

from .utilities import load_config


@pytest.fixture(scope="session")
def config():
    return load_config("libvirt_config.json")


@pytest.fixture
def client(config):
    LibvirtClient = pytest.importorskip("katprep.clients.LibvirtClient")

    return LibvirtClient.LibvirtClient(
        logging.ERROR,
        config["config"]["uri"],
        config["config"]["api_user"],
        config["config"]["api_pass"]
    )


def test_invalid_login(config):
    """
    Ensure exceptions on invalid logins
    """
    LibvirtClient = pytest.importorskip("katprep.clients.LibvirtClient")

    with pytest.raises(InvalidCredentialsException):
        LibvirtClient.LibvirtClient(
            logging.ERROR,
            config["config"]["uri"],
            "giertz", "paulapinkepank"
        )

        # TODO: make a call?
        # api_dummy.get_vm_ips


def test_create_snapshot_fail(virtClient, nonexisting_vm, snapshot_name):
    """
    Ensure that creating snapshots of non-existing VMs is not possible
    """
    with pytest.raises(SessionException):
        virtClient.create_snapshot(nonexisting_vm, snapshot_name, snapshot_name)


def test_remove_snapshot_fail(virtClient, nonexisting_vm, snapshot_name):
    """
    Ensure that removing snapshots of non-existing VMs is not possible
    """
    with pytest.raises(SessionException):
        virtClient.remove_snapshot(nonexisting_vm, snapshot_name)


def test_has_snapshot_fail(virtClient, nonexisting_vm, snapshot_name):
    """
    Ensure that checking non-existing VMs for snapshots is not possible
    """
    with pytest.raises(EmptySetException):
        virtClient.has_snapshot(nonexisting_vm, snapshot_name)


def test_revert_snapshot_fail(virtClient, nonexisting_vm, snapshot_name):
    """
    Ensure that reverting non-existing snapshots is not possible
    """
    with pytest.raises(SessionException):
        virtClient.revert_snapshot(nonexisting_vm, snapshot_name)


def test_snapshot_handling(virtClient, config, snapshot_name):
    host = config["valid_objects"]["vm"]
    virtClient.create_snapshot(host, snapshot_name, snapshot_name)

    try:
        virtClient.revert_snapshot(host, snapshot_name)

        try:
            assert virtClient.has_snapshot(host, snapshot_name)
        except EmptySetException as err:
            print(err)
    finally:
        virtClient.remove_snapshot(host, snapshot_name)
