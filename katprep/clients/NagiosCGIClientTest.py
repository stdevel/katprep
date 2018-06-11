#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Nagios/Icinga 1.x CGI integration
"""

import os
import time
import unittest
import logging
from NagiosCGIClient import NagiosCGIClient, SessionException, \
UnsupportedRequest

class NagiosCGIClientTest(unittest.TestCase):
    """
    NagiosCGIClient test cases
    """
    cgi_icinga = None
    """
    NagiosCGIClient: Nagios CGI client (for Icinga)
    """
    cgi_nagios = None
    """
    NagiosCGIClient: Nagios CGI client (for legacy)
    """
    HOSTNAME = os.environ["HOSTNAME"]
    """
    str: FQDN of a Icinga system
    """
    LEGACY_HOSTNAME = os.environ["LEGACY_HOSTNAME"]
    """
    str: FQDN of a Nagios system
    """
    CGI_USER = os.environ["API_USER"]
    """
    str: CGI username
    """
    CGI_PASS = os.environ["API_PASS"]
    """
    str: CGI password
    """
    HOST = os.environ["HOST"]
    """
    str: host for scheduling/removing downtimes
    """
    HOST_SERVICE = os.environ["HOST_SERVICE"]
    """
    str: existing service for a particular host
    """
    HOST_SERVICES = int(os.environ["HOST_SERVICES"])
    """
    int: amount of services monitored
    """
    HOSTGROUP = os.environ["HOSTGROUP"]
    """
    str: hostgroup for scheduling downtimes
    """



    def setUp(self):
        """
        Connecting the interfaces
        """
        #Legacy
        self.cgi_nagios = NagiosCGIClient(
            logging.DEBUG, self.LEGACY_HOSTNAME,
            self.CGI_USER, self.CGI_PASS,
            verify=False
        )
        #Icinga
        self.cgi_icinga = NagiosCGIClient(
            logging.DEBUG, self.HOSTNAME,
            self.CGI_USER, self.CGI_PASS,
            verify=False
        )

    #TODO
    #def hostname!!



    def test_valid_login(self):
        """
        Ensure exceptions on valid logins
        """
        #dummy call
        self.cgi_icinga.get_hosts()

    def test_valid_loginleg(self):
        """
        Ensure exceptions on valid logins
        """
        #dummy call
        self.cgi_nagios.get_hosts()



    def test_invalid_login(self):
        """
        Ensure exceptions on invalid logins
        """
        with self.assertRaises(SessionException):
            cgi_dummy = NagiosCGIClient(
                logging.DEBUG, self.HOSTNAME,
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
                logging.DEBUG, self.HOSTNAME,
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
        self.cgi_icinga.schedule_downtime(self.HOST, "host")
        #wait as it might take some time to see downtime in CGI
        time.sleep(10)

    def test_schedule_downtime_host_leg(self):
        """
        Ensure that downtimes can be scheduled, even on ancient systems
        """
        #schedule downtime
        self.cgi_nagios.schedule_downtime(self.HOST, "host")
        #wait as it might take some time to see downtime in CGI
        time.sleep(10)

    def test_has_downtime(self):
        """
        Ensure that checking downtime is working
        """
        self.assertTrue(
            self.cgi_icinga.has_downtime(self.HOST)
        )

    def test_has_downtimeleg(self):
        """
        Ensure that checking downtime is working
        """
        self.assertTrue(
            self.cgi_nagios.has_downtime(self.HOST)
        )



    def test_unschedule_downtime_host(self):
        """
        Ensure that unscheduling downtimes for hosts is working
        """
        self.assertTrue(
            self.cgi_icinga.remove_downtime(self.HOST)
        )

    def test_schedule_downtime_hostgrp(self):
        """
        Ensure that scheduling downtimes for hostgroups is working
        """
        self.assertTrue(
            self.cgi_icinga.schedule_downtime(self.HOSTGROUP, "hostgroup")
        )



    def test_unsupported_request(self):
        """
        Ensure unsupported calls on Nagios will die in a fire
        """
        with self.assertRaises(UnsupportedRequest):
            #try to remove downtime
            self.cgi_nagios.remove_downtime("dummy")



    def test_get_hosts(self):
        """
        Ensure that receiving hosts is possible
        """
        hosts = self.cgi_icinga.get_hosts()
        self.assertTrue(
            self.HOST in str(hosts)
        )

    def test_get_hostsleg(self):
        """
        Ensure that receiving hosts is possible
        """
        hosts = self.cgi_nagios.get_hosts()
        self.assertTrue(
            self.HOST in str(hosts)
        )



    def test_get_services(self):
        """
        Ensure that hosts include existing services
        """
        services = self.cgi_icinga.get_services(
            self.HOST, only_failed=False
        )
        self.assertTrue(
            bool(
                self.HOST_SERVICE in str(services) and \
                len(services) == self.HOST_SERVICES
            )
        )

    def test_get_servicesleg(self):
        """
        Ensure that hosts include existing services
        """
        services = self.cgi_nagios.get_services(
            self.HOST, only_failed=False
        )
        self.assertTrue(
            self.HOST_SERVICE in str(services) and \
            len(services) == self.HOST_SERVICES
        )

    #def test_get_failed_services(self):



if __name__ == "__main__":
    #do not sort test cases as there are dependencies
    unittest.sortTestMethodsUsing = None
    unittest.main()
