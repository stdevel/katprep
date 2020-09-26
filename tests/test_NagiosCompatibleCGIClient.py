#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Nagios/Icinga 1.x CGI integration
"""

from __future__ import absolute_import

import logging
import time
import pytest

from katprep.clients.NagiosCGIClient import NagiosCGIClient
from katprep.clients import SessionException, UnsupportedRequestException

from .utilities import load_config


@pytest.fixture(
    params=["main", "legacy"],
    ids=["Icinga 1", "Nagios"]
)
def nagios_type(request):
    return request.param


@pytest.fixture(scope='session')
def config():
    return load_config("nagios_config.json")


@pytest.fixture
def monitoring_client(config, nagios_type):
    try:
        yield NagiosCGIClient(
            logging.ERROR,
            config[nagios_type]["hostname"],
            config[nagios_type]["cgi_user"],
            config[nagios_type]["cgi_pass"],
            verify=False
        )
    finally:
        time.sleep(8)


@pytest.fixture
def icinga_client(config):
    try:
        yield NagiosCGIClient(
            logging.ERROR,
            config["main"]["hostname"],
            config["main"]["cgi_user"],
            config["main"]["cgi_pass"],
            verify=False
        )
    finally:
        time.sleep(8)


@pytest.fixture
def nagios_client(config):
    try:
        yield NagiosCGIClient(
            logging.ERROR,
            config["legacy"]["hostname"],
            config["legacy"]["cgi_user"],
            config["legacy"]["cgi_pass"],
            verify=False
        )
    finally:
        time.sleep(8)


def test_valid_login(monitoring_client):
    """
    Ensure exceptions on valid logins
    """
    monitoring_client.is_authenticated()


def test_invalid_login(config, nagios_type):
    """
    Ensure exceptions on invalid logins
    """
    with pytest.raises(SessionException):
        client = NagiosCGIClient(
            logging.ERROR,
            config[nagios_type]["hostname"],
            "giertz",
            "paulapinkepank",
            verify=False
        )
        client.is_authenticated()


def test_scheduling_downtime_for_host(monitoring_client, config, nagios_type):
    """
    Testing downtime scheduling.

    Ensure that downtimes can be scheduled, even on ancient systems.
    Ensure that checking downtime is working.
    For Icinga we also ensure that unscheduling downtimes works.
    """
    host = config[nagios_type]["host"]
    monitoring_client.schedule_downtime(host, "host")
    assert monitoring_client.has_downtime(host)

    if nagios_type == 'main':  # Icinga
        assert monitoring_client.remove_downtime(host)
    else:  # Nagios
        with pytest.raises(UnsupportedRequestException):
            # try to remove downtime
            monitoring_client.remove_downtime("dummy")


def test_schedule_downtime_hostgrp(icinga_client, config):
    """
    Ensure that scheduling downtimes for hostgroups is working
    """
    hostgroup = config["main"]["hostgroup"]
    assert icinga_client.schedule_downtime(hostgroup, "hostgroup")


def test_get_hosts(monitoring_client, config, nagios_type):
    """
    Ensure that receiving hosts is possible
    """
    hosts = monitoring_client.get_hosts()
    assert config[nagios_type]["host"] in [host['name'] for host in hosts]


def test_get_services(monitoring_client, config, nagios_type):
    """
    Ensure that hosts include existing services
    """
    services = monitoring_client.get_services(
        config[nagios_type]["host"], only_failed=False
    )
    assert config[nagios_type]["host_service"] in [service['name'] for service in services]
    assert len(services) == config[nagios_type]["host_services"]
