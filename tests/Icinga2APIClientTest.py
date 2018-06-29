#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Icinga2 API integration
"""

import os
import time
import unittest
import logging
import json
from katprep.clients.Icinga2APIClient import Icinga2APIClient
from katprep.clients import SessionException, EmptySetException



class Icinga2APIClientTest(unittest.TestCase):
    """
    Icinga2APIClient test cases
    """
    LOGGER = logging.getLogger('Icinga2APIClientTest')
    """
    logging: Logger instance
    """
    api_icinga = None
    """
    Icinga2APIClient: Icinga2 API client
    """
    config = None
    """
    str: JSON object containing valid hosts and services
    """
    set_up = False
    """
    bool: Flag whether the connection was set up
    """



    def setUp(self):
        """
        Connecting the interfaces
        """
        if not self.set_up:
            #instance logging
            logging.basicConfig()
            self.LOGGER.setLevel(logging.DEBUG)
            #reading configuration
            try:
                with open("icinga2_config.json", "r") as json_file:
                    json_data = json_file.read().replace("\n", "")
                self.config = json.loads(json_data)
            except IOError as err:
                self.LOGGER.error(
                    "Unable to read configuration file: '%s'", err
                )
            #instance API client
            self.api_icinga = Icinga2APIClient(
                logging.ERROR, self.config["config"]["hostname"],
                self.config["config"]["api_user"],
                self.config["config"]["api_pass"]
            )
            self.set_up = True



    def tearDown(self):
        """
        Function that is executed after every test
        """
        #wait for changes to be applied
        time.sleep(30)



    def test_valid_login(self):
        """
        Ensure exceptions on valid logins
        """
        #dummy call
        self.api_icinga.dummy_call()

    def test_invalid_login(self):
        """
        Ensure exceptions on invalid logins
        """
        with self.assertRaises(SessionException):
            api_dummy = Icinga2APIClient(
                logging.ERROR, self.config["config"]["hostname"],
                "giertz", "paulapinkepank"
            )
            #dummy call
            api_dummy.dummy_call()



    def test_sched_dt_host(self):
        """
        Ensure that host downtimes can be scheduled
        """
        self.api_icinga.schedule_downtime(
            self.config["valid_objects"]["host"], "host"
        )

    def test_sched_dt_host_fail(self):
        """
        Ensure that host downtimes cannot be scheduled when using invalid hosts
        """
        with self.assertRaises(EmptySetException):
            self.api_icinga.schedule_downtime(
                "giertz.pinkepank.loc", "host"
            )



    def test_sched_dt_hostgrp(self):
        """
        Ensure that hostgroup downtimes can be scheduled
        """
        self.assertTrue(
            self.api_icinga.schedule_downtime(
                self.config["valid_objects"]["hostgroup"],
                "hostgroup"
            )
        )

    def test_sched_dt_hostgrp_fail(self):
        """
        Ensure that hostgroup downtimes cannot be scheduled with invalid names
        """
        with self.assertRaises(EmptySetException):
            self.api_icinga.schedule_downtime(
                "giertz.pinkepank.loc", "hostgroup"
            )



    def test_sched_has_downtime(self):
        """
        Ensure that checking downtime is working
        """
        self.assertTrue(
            self.api_icinga.has_downtime(
                self.config["valid_objects"]["host"]
            )
        )

    def test_sched_has_downtime_fail(self):
        """
        Ensure that checking downtime fails for non-existing hosts
        """
        with self.assertRaises(EmptySetException):
            self.api_icinga.has_downtime(
                "giertz.pinkepank.loc"
            )



    def test_unsched_dt_host(self):
        """
        Ensure that unscheduling downtimes for hosts is working
        """
        self.assertTrue(
            self.api_icinga.remove_downtime(
                self.config["valid_objects"]["host"], "host"
            )
        )

    def test_unsched_dt_host_fail(self):
        """
        Ensure that unscheduling downtimes fails for non-existing hosts
        """
        with self.assertRaises(EmptySetException):
            self.api_icinga.remove_downtime(
                "giertz.pinkepank.loc", "host"
            )



    def test_unsched_dt_hostgrp(self):
        """
        Ensure that unscheduling downtimes for hostgroups is working
        """
        self.assertTrue(
            self.api_icinga.remove_downtime(
                self.config["valid_objects"]["hostgroup"], "hostgroup"
            )
        )

    def test_unsched_dt_hostgrp_fail(self):
        """
        Ensure that unscheduling downtimes fails for non-existing hostgroups
        """
        with self.assertRaises(EmptySetException):
            self.api_icinga.remove_downtime(
                "giertz-hosts", "hostgroup"
            )



    def test_get_hosts(self):
        """
        Ensure that receiving hosts is possible
        """
        self.assertTrue(
            self.config["valid_objects"]["host"] in str(self.api_icinga.get_hosts())
        )



    def test_get_services(self):
        """
        Ensure that hosts include existing services
        """
        services = self.api_icinga.get_services(
            self.config["valid_objects"]["host"], only_failed=False
        )
        self.assertTrue(
            str(self.config["valid_objects"]["host_service"]) in str(services)
        )

    def test_get_services_fail(self):
        """
        Ensure that checking services of non-existing hosts fails
        """
        with self.assertRaises(EmptySetException):
            self.api_icinga.get_services(
                "giertz.pinkepank.loc", only_failed=False
            )



if __name__ == "__main__":
    #start tests or die in a fire
    if not os.path.isfile("icinga2_config.json"):
        print "Please create configuration file icinga2_config.json!"
        exit(1)
    else:
        #do not sort test cases as there are dependencies
        unittest.sortTestMethodsUsing = None
        unittest.main()
