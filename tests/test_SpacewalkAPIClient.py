#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Spacewalk API integration
"""

import os
import logging
import json
import ssl
import pytest
import mock
from katprep.clients.SpacewalkAPIClient import SpacewalkAPIClient
from katprep.clients import (APILevelNotSupportedException,
                             InvalidCredentialsException)


@pytest.fixture(scope='session')
def config():
    config_file = "spw_config.json"
    if not os.path.isfile(config_file):
        pytest.skip("Please create configuration file %s!" % config_file)

    try:
        with open(config_file, "r") as json_file:
            return json.load(json_file)
    except IOError as err:
        pytest.skip("Unable to read configuration file: '%s'", err)


@pytest.fixture
def client(config):
    # TODO: Instance client
    pytest.skip('Diggi, bau mich ein!')


def test_invalid_login(config):
    """
    Ensure exceptions on invalid logins
    """
    with pytest.raises(InvalidCredentialsException):
        SpacewalkAPIClient(
            logging.ERROR,
            config["config"]["hostname"],
            "giertz",
            "paulapinkepank"
        )


def test_deny_legacy(config):
    """
    Ensure that old Spacewalk APIs are refused
    """
    with mock.patch('ssl._create_default_https_context',
                    ssl._create_unverified_context):
        # we really need to skip SSL verification for old versions

        with pytest.raises(APILevelNotSupportedException):
            SpacewalkAPIClient(
                logging.ERROR,
                config["config"]["hostname_legacy"],
                config["config"]["api_user"],
                config["config"]["api_pass"],
            )
