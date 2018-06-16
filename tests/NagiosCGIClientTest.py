#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Nagios/Icinga 1.x CGI integration
"""

import os
import time
import unittest
import logging
import json
from katprep.clients.NagiosCGIClient import NagiosCGIClient
from katprep.clients import SessionException, UnsupportedRequestException

class NagiosCGIClientTest(unittest.TestCase):
    """
    NagiosCGIClient test cases
    """
    LOGGER = logging.getLogger('NagiosCGIClientTest')
    """
    logging: Logger instance
    """
    cgi_icinga = None
    """
    NagiosCGIClient: Nagios CGI client (for Icinga)
    """
    cgi_nagios = None
    """
    NagiosCGIClient: Nagios CGI client (for legacy)
    """
    config = None
    """
    str: JSON object containing valid hosts and services
    """



    def setUp(self):
        """
        Connecting the interfaces
        """
        #instance logging
        logging.basicConfig()
        self.LOGGER.setLevel(logging.DEBUG)
        #reading configuration
        try:
            with open("nagios_config.json", "r") as json_file:
                json_data = json_file.read().replace("\n", "")
            self.config = json.loads(json_data)
        except IOError as err:
            self.LOGGER.error(
                "Unable to read configuration file: '%s'", err
            )
        #Legacy
        self.cgi_nagios = NagiosCGIClient(
            logging.ERROR, self.config["legacy"]["hostname"],
            self.config["legacy"]["cgi_user"],
            self.config["legacy"]["cgi_pass"],
            verify=False
        )
        #Icinga
        self.cgi_icinga = NagiosCGIClient(
            logging.ERROR, self.config["main"]["hostname"],
            self.config["main"]["cgi_user"],
            self.config["main"]["cgi_pass"],
            verify=False
        )



    def test_valid_login(self):
        """
        Ensure exceptions on valid logins
        """
        #dummy call
        self.cgi_icinga.dummy_call()

    def test_valid_loginleg(self):
        """
        Ensure exceptions on valid logins
        """
        #dummy call
        self.cgi_icinga.dummy_call()



    def test_invalid_login(self):
        """
        Ensure exceptions on invalid logins
        """
        with self.assertRaises(SessionException):
            cgi_dummy = NagiosCGIClient(
                logging.ERROR, self.config["main"]["hostname"],
                "giertz", "paulapinkepank",
                verify=False
            )
            #dummy call
            cgi_dummy.get_hosts()

    def test_invalid_loginleg(self):
        """
        Ensure exceptions on invalid logins
        """
        with self.assertRaises(SessionException):
            cgi_dummy = NagiosCGIClient(
                logging.ERROR, self.config["legacy"]["hostname"],
                "giertz", "paulapinkepank",
                verify=False
            )
            #dummy call
            cgi_dummy.get_hosts()



    def test_schedule_downtime_host(self):
        """
        Ensure that downtimes can be scheduled
        """
        #schedule downtime
        self.cgi_icinga.schedule_downtime(
            self.config["main"]["host"], "host"
        )
        #wait as it might take some time to see downtime in CGI
        time.sleep(30)

    def test_schedule_downtime_host_leg(self):
        """
        Ensure that downtimes can be scheduled, even on ancient systems
        """
        #schedule downtime
        self.cgi_nagios.schedule_downtime(
            self.config["legacy"]["host"], "host"
        )
        #wait as it might take some time to see downtime in CGI
        time.sleep(30)

    def test_has_downtime(self):
        """
        Ensure that checking downtime is working
        """
        self.assertTrue(
            self.cgi_icinga.has_downtime(
                self.config["main"]["host"]
            )
        )

    def test_has_downtimeleg(self):
        """
        Ensure that checking downtime is working
        """
        self.assertTrue(
            self.cgi_nagios.has_downtime(
                self.config["legacy"]["host"]
            )
        )



    def test_unsched_downtime_host(self):
        """
        Ensure that unscheduling downtimes for hosts is working
        """
        self.assertTrue(
            self.cgi_icinga.remove_downtime(
                self.config["main"]["host"]
            )
        )

    def test_schedule_downtime_hostgrp(self):
        """
        Ensure that scheduling downtimes for hostgroups is working
        """
        self.assertTrue(
            self.cgi_icinga.schedule_downtime(
                self.config["legacy"]["hostgroup"], "hostgroup"
            )
        )



    def test_unsupported_request(self):
        """
        Ensure unsupported calls on Nagios will die in a fire
        """
        with self.assertRaises(UnsupportedRequestException):
            #try to remove downtime
            self.cgi_nagios.remove_downtime("dummy")



    def test_get_hosts(self):
        """
        Ensure that receiving hosts is possible
        """
        hosts = self.cgi_icinga.get_hosts()
        self.assertTrue(
            self.config["main"]["host"] in str(hosts)
        )

    def test_get_hostsleg(self):
        """
        Ensure that receiving hosts is possible
        """
        hosts = self.cgi_nagios.get_hosts()
        self.assertTrue(
            self.config["legacy"]["host"] in str(hosts)
        )



    def test_get_services(self):
        """
        Ensure that hosts include existing services
        """
        services = self.cgi_icinga.get_services(
            self.config["main"]["host"], only_failed=False
        )
        self.assertTrue(
            bool(
                self.config["main"]["host_service"] in str(services) and \
                len(services) == self.config["main"]["host_services"]
            )
        )

    def test_get_servicesleg(self):
        """
        Ensure that hosts include existing services
        """
        services = self.cgi_nagios.get_services(
            self.config["legacy"]["host"], only_failed=False
        )
        self.assertTrue(
            self.config["legacy"]["host_service"] in str(services) and \
            len(services) == self.config["legacy"]["host_services"]
        )

    #def test_get_failed_services(self):



if __name__ == "__main__":
    #start tests or die in a fire
    if not os.path.isfile("nagios_config.json"):
        print "Please create configuration file nagios_config.json!"
        exit(1)
    else:
        #do not sort test cases as there are dependencies
        unittest.sortTestMethodsUsing = None
        unittest.main()
