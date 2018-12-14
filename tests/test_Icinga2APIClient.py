#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Icinga2 API integration
"""

from __future__ import absolute_import

import logging
import pytest
from katprep.clients.Icinga2APIClient import Icinga2APIClient
from katprep.clients import EmptySetException, SessionException

from .utilities import load_config


@pytest.fixture
def config():
    return load_config("icinga2_config.json")


@pytest.fixture
def client(config):
    return Icinga2APIClient(
        logging.ERROR,
        config["config"]["hostname"],
        config["config"]["api_user"],
        config["config"]["api_pass"]
    )


def test_valid_login(client):
    """
    Ensure exceptions on valid logins
    """
    client.dummy_call()


def test_invalid_login(config):
    """
    Ensure exceptions on invalid logins
    """
    with pytest.raises(SessionException):
        client = Icinga2APIClient(
            logging.ERROR,
            config["config"]["hostname"],
            "giertz",
            "paulapinkepank"
        )
        client.dummy_call()


def test_scheduling_downtime_for_host(client, config):
    """
    Ensure that host downtimes can be scheduled
    """
    host = config["valid_objects"]["host"]
    client.schedule_downtime(host, "host")
    assert client.has_downtime(host)
    assert client.remove_downtime(host, "host")


def test_sched_dt_host_fail(client, config):
    """
    Ensure that host downtimes cannot be scheduled when using invalid hosts
    """
    with pytest.raises(EmptySetException):
        client.schedule_downtime("giertz.pinkepank.loc", "host")


def test_schedule_downtime_for_hostgrp(client, config):
    """
    Ensure that hostgroup downtimes can be scheduled
    """
    hostgroup = config["valid_objects"]["hostgroup"]
    assert client.schedule_downtime(hostgroup, "hostgroup")
    assert client.remove_downtime(hostgroup, "hostgroup")


def test_sched_dt_hostgrp_fail(client):
    """
    Ensure that hostgroup downtimes cannot be scheduled with invalid names
    """
    with pytest.raises(EmptySetException):
        client.schedule_downtime("giertz.pinkepank.loc", "hostgroup")


def test_sched_has_downtime_fail(client):
    """
    Ensure that checking downtime fails for non-existing hosts
    """
    with pytest.raises(EmptySetException):
        client.has_downtime("giertz.pinkepank.loc")


def test_unsched_dt_host_fail(client):
    """
    Ensure that unscheduling downtimes fails for non-existing hosts
    """
    with pytest.raises(SessionException):
        client.remove_downtime("giertz.pinkepank.loc", "host")


def test_unsched_dt_hostgrp_fail(client):
    """
    Ensure that unscheduling downtimes fails for non-existing hostgroups
    """
    with pytest.raises(SessionException):
        client.remove_downtime("giertz-hosts", "hostgroup")


def test_get_hosts(client, config):
    """
    Ensure that receiving hosts is possible
    """
    hosts = client.get_hosts()
    assert config["valid_objects"]["host"] in [host['name'] for host in hosts]


def test_get_services(client, config):
    """
    Ensure that hosts include existing services
    """
    services = client.get_services(
        config["valid_objects"]["host"],
        only_failed=False
    )
    assert config["valid_objects"]["host_service"] in [service['name'] for service in services]


def test_get_services_fail(client):
    """
    Ensure that checking services of non-existing hosts fails
    """
    with pytest.raises(EmptySetException):
        client.get_services("giertz.pinkepank.loc", only_failed=False)
