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
    cgi_nagios = None
    """
    NagiosCGIClient: Nagios CGI client (for legacy)
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
        #only set-up _all_ the stuff once
        if not self.set_up:
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
        self.cgi_nagios.dummy_call()

    def test_invalid_login(self):
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
            cgi_dummy.dummy_call()



    def test_schedule_downtime_host(self):
        """
        Ensure that downtimes can be scheduled, even on ancient systems
        """
        #schedule downtime
        self.cgi_nagios.schedule_downtime(
            self.config["legacy"]["host"], "host"
        )

    def test_has_downtime(self):
        """
        Ensure that checking downtime is working
        """
        self.assertTrue(
            self.cgi_nagios.has_downtime(
                self.config["legacy"]["host"]
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
        hosts = self.cgi_nagios.get_hosts()
        self.assertTrue(
            self.config["legacy"]["host"] in str(hosts)
        )



    def test_get_services(self):
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



if __name__ == "__main__":
    #start tests or die in a fire
    if not os.path.isfile("nagios_config.json"):
        print "Please create configuration file nagios_config.json!"
        exit(1)
    else:
        #do not sort test cases as there are dependencies
        unittest.sortTestMethodsUsing = None
        unittest.main()
