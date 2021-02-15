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
    system_id = client.get_host_id(config["valid_objects"]["host"]["name"])
    assert system_id == config["valid_objects"]["host"]["id"]


def test_get_host_id_invalid(client):
    """
    Ensure that host ID cannot retrieved by invalid name
    """
    with pytest.raises(EmptySetException):
        client.get_host_id("web%s" % random.randint(800, 1500))


def test_get_hostparams(client, config):
    """
    Ensure that host params can be retrieved
    """
    hostparams = client.get_host_params(config["valid_objects"]["host"]["id"])
    for key, value in config["valid_objects"]["hostparams"].items():
        assert hostparams[key] == value


def test_get_hostparams_invalid(client):
    """
    Ensure that host params cannot be retrieved by supplying invalid IDs
    """
    with pytest.raises(SessionException):
        client.get_host_params(random.randint(800, 1500))
