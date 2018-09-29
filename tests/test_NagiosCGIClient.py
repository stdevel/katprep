#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Nagios/Icinga 1.x CGI integration
"""

import os
import time
import logging
import json
import pytest
from katprep.clients.NagiosCGIClient import NagiosCGIClient
from katprep.clients import SessionException, UnsupportedRequestException


@pytest.fixture(scope='session')
def config():
    config_file = "nagios_config.json"
    if not os.path.isfile(config_file):
        pytest.skip("Please create configuration file %s!" % config_file)

    try:
        with open(config_file, "r") as json_file:
            return json.load(json_file)
    except IOError as err:
        pytest.skip("Unable to read configuration file: '%s'", err)


@pytest.fixture
def nagiosClient(config):
    try:
        yield NagiosCGIClient(
            logging.ERROR,
            config["legacy"]["hostname"],
            config["legacy"]["cgi_user"],
            config["legacy"]["cgi_pass"],
            verify=False
        )
    finally:
        time.sleep(30)


def test_valid_login(nagiosClient):
    """
    Ensure exceptions on valid logins
    """
    nagiosClient.dummy_call()


def test_invalid_login(config):
    """
    Ensure exceptions on invalid logins
    """
    with pytest.raises(SessionException):
        client = NagiosCGIClient(
            logging.ERROR,
            config["legacy"]["hostname"],
            "giertz",
            "paulapinkepank",
            verify=False
        )
        client.dummy_call()


def test_scheduling_downtime_for_host(nagiosClient, config):
    """
    Testing downtime scheduling.

    Ensure that downtimes can be scheduled, even on ancient systems.
    Ensure that checking downtime is working.
    """
    host = config["legacy"]["host"]
    nagiosClient.schedule_downtime(host, "host")
    assert nagiosClient.has_downtime(host)


def test_unsupported_request(nagiosClient):
    """
    Ensure unsupported calls on Nagios will die in a fire
    """
    with pytest.raises(UnsupportedRequestException):
        # try to remove downtime
        nagiosClient.remove_downtime("dummy")


def test_get_hosts(nagiosClient, config):
    """
    Ensure that receiving hosts is possible
    """
    hosts = nagiosClient.get_hosts()
    assert config["legacy"]["host"] in str(hosts)


def test_get_services(nagiosClient, config):
    """
    Ensure that hosts include existing services
    """
    services = nagiosClient.get_services(
        config["legacy"]["host"], only_failed=False
    )
    assert config["legacy"]["host_service"] in str(services)
    assert len(services) == config["legacy"]["host_services"]
