#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Libvirt integration
"""

from __future__ import absolute_import, print_function

import logging
import pytest
from katprep.clients import (EmptySetException, InvalidCredentialsException,
                             SessionException)

from .utilities import load_config


@pytest.fixture(scope="session")
def config():
    return load_config("libvirt_config.json")


@pytest.fixture
def client(config):
    libvirt_client = pytest.importorskip("katprep.clients.libvirt_client")

    return libvirt_client.LibvirtClient(
        logging.ERROR,
        config["config"]["uri"],
        config["config"]["api_user"],
        config["config"]["api_pass"]
    )


def test_invalid_login(config):
    """
    Ensure exceptions on invalid logins
    """
    libvirt_client = pytest.importorskip("katprep.clients.libvirt_client")

    with pytest.raises(InvalidCredentialsException):
        libvirt_client.LibvirtClient(
            logging.ERROR,
            config["config"]["uri"],
            "giertz", "paulapinkepank"
        )

        # TODO: make a call?
        # api_dummy.get_vm_ips


def test_create_snapshot_fail(virt_client, nonexisting_vm, snapshot_name):
    """
    Ensure that creating snapshots of non-existing VMs is not possible
    """
    with pytest.raises(SessionException):
        virt_client.create_snapshot(nonexisting_vm, snapshot_name, snapshot_name)


def test_remove_snapshot_fail(virt_client, nonexisting_vm, snapshot_name):
    """
    Ensure that removing snapshots of non-existing VMs is not possible
    """
    with pytest.raises(SessionException):
        virt_client.remove_snapshot(nonexisting_vm, snapshot_name)


def test_has_snapshot_fail(virt_client, nonexisting_vm, snapshot_name):
    """
    Ensure that checking non-existing VMs for snapshots is not possible
    """
    with pytest.raises(EmptySetException):
        virt_client.has_snapshot(nonexisting_vm, snapshot_name)


def test_revert_snapshot_fail(virt_client, nonexisting_vm, snapshot_name):
    """
    Ensure that reverting non-existing snapshots is not possible
    """
    with pytest.raises(SessionException):
        virt_client.revert_snapshot(nonexisting_vm, snapshot_name)


def test_snapshot_handling(virt_client, config, snapshot_name):
    host = config["valid_objects"]["vm"]
    virt_client.create_snapshot(host, snapshot_name, snapshot_name)

    try:
        virt_client.revert_snapshot(host, snapshot_name)

        try:
            assert virt_client.has_snapshot(host, snapshot_name)
        except EmptySetException as err:
            print(err)
    finally:
        virt_client.remove_snapshot(host, snapshot_name)
