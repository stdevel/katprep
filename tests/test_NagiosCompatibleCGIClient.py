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
def nagiosType(request):
    return request.param


@pytest.fixture(scope='session')
def config():
    return load_config("nagios_config.json")


@pytest.fixture
def monitoringClient(config, nagiosType):
    try:
        yield NagiosCGIClient(
            logging.ERROR,
            config[nagiosType]["hostname"],
            config[nagiosType]["cgi_user"],
            config[nagiosType]["cgi_pass"],
            verify=False
        )
    finally:
        time.sleep(30)


@pytest.fixture
def icingaClient(config):
    try:
        yield NagiosCGIClient(
            logging.ERROR,
            config["main"]["hostname"],
            config["main"]["cgi_user"],
            config["main"]["cgi_pass"],
            verify=False
        )
    finally:
        time.sleep(30)


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


def test_valid_login(monitoringClient):
    """
    Ensure exceptions on valid logins
    """
    monitoringClient.dummy_call()


def test_invalid_login(config, nagiosType):
    """
    Ensure exceptions on invalid logins
    """
    with pytest.raises(SessionException):
        client = NagiosCGIClient(
            logging.ERROR,
            config[nagiosType]["hostname"],
            "giertz",
            "paulapinkepank",
            verify=False
        )
        client.dummy_call()


def test_scheduling_downtime_for_host(monitoringClient, config, nagiosType):
    """
    Testing downtime scheduling.

    Ensure that downtimes can be scheduled, even on ancient systems.
    Ensure that checking downtime is working.
    For Icinga we also ensure that unscheduling downtimes works.
    """
    host = config[nagiosType]["host"]
    monitoringClient.schedule_downtime(host, "host")
    assert monitoringClient.has_downtime(host)

    if nagiosType == 'main':  # Icinga
        assert monitoringClient.remove_downtime(host)
    else:  # Nagios
        with pytest.raises(UnsupportedRequestException):
            # try to remove downtime
            monitoringClient.remove_downtime("dummy")


def test_schedule_downtime_hostgrp(icingaClient, config):
    """
    Ensure that scheduling downtimes for hostgroups is working
    """
    hostgroup = config["main"]["hostgroup"]
    assert icingaClient.schedule_downtime(hostgroup, "hostgroup")


def test_get_hosts(monitoringClient, config, nagiosType):
    """
    Ensure that receiving hosts is possible
    """
    hosts = nagiosClient.get_hosts()
    assert config[nagiosType]["host"] in hosts


def test_get_services(monitoringClient, config, nagiosType):
    """
    Ensure that hosts include existing services
    """
    services = monitoringClient.get_services(
        config[nagiosType]["host"], only_failed=False
    )
    assert config[nagiosType]["host_service"] in services
    assert len(services) == config[nagiosType]["host_services"]
