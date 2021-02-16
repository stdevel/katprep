#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Uyuni API integration
"""

from __future__ import absolute_import

import logging
import random
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


def test_get_host_id(client, config):
    """
    Ensure that host ID can retrieved by name
    """
    system_id = client.get_host_id(
        config["valid_objects"]["host"]["name"]
    )
    assert system_id == config["valid_objects"]["host"]["id"]


def test_get_host_id_invalid(client):
    """
    Ensure that host ID cannot retrieved by invalid name
    """
    with pytest.raises(EmptySetException):
        client.get_host_id("web%s" % random.randint(800, 1500))


def test_get_host_params(client, config):
    """
    Ensure that host params can be retrieved
    """
    host_params = client.get_host_params(
        config["valid_objects"]["host"]["id"]
    )
    for key, value in config["valid_objects"]["hostparams"].items():
        assert host_params[key] == value


def test_get_host_params_invalid(client):
    """
    Ensure that host params cannot be retrieved by supplying invalid IDs
    """
    with pytest.raises(SessionException):
        client.get_host_params(random.randint(800, 1500))


def test_get_host_patches(client, config):
    """
    Ensure that host patches can be found
    """
    host_patches = client.get_host_patches(
        config["valid_objects"]["host"]["id"]
    )
    assert len(host_patches) > 0


def test_get_host_patches_invalid(client):
    """
    Ensure that patches for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_patches(random.randint(800, 1500))


def test_get_host_upgrades(client, config):
    """
    Ensure that host package upgrades can be found
    """
    host_upgrades = client.get_host_upgrades(
        config["valid_objects"]["host"]["id"]
    )
    assert len(host_upgrades) > 0


def test_get_host_upgrades_invalid(client):
    """
    Ensure that package upgrades for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_upgrades(random.randint(800, 1500))


def test_get_host_groups(client, config):
    """
    Ensure that host groups can be found
    """
    host_groups = client.get_host_groups(
        config["valid_objects"]["host"]["id"]
    )
    _groups = [x['system_group_name'] for x in host_groups]
    assert config["valid_objects"]["host"]["group"] in _groups


def test_get_host_groups_invalid(client):
    """
    Ensure that host groups for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_groups(random.randint(800, 1500))


def test_get_host_details(client, config):
    """
    Ensure that host details can be found
    """
    host_details = client.get_host_details(
        config["valid_objects"]["host"]["id"]
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


def test_get_host_details_invalid(client):
    """
    Ensure that details for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_details(random.randint(800, 1500))


def test_host_tasks(client, config):
    """
    Ensure that host tasks can be found
    """
    host_tasks = client.get_host_tasks(
        config["valid_objects"]["host"]["id"]
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


def test_host_tasks_invalid(client):
    """
    Ensure that tasks for invalid hosts cannot be gathered
    """
    with pytest.raises(SessionException):
        client.get_host_tasks(random.randint(800, 1500))
