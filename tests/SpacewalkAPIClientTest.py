#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Spacewalk API integration
"""

import os
import unittest
import logging
import json
import ssl
from katprep.clients.SpacewalkAPIClient import SpacewalkAPIClient
from katprep.clients import *

class SpacewalkAPIClientTest(unittest.TestCase):
    """
    SpacewalkAPIClient test cases
    """
    api_spacewalk = None
    """
    SpacewalkAPIClient: Spacewalk API client
    """
    LOGGER = logging.getLogger('SpacewalkAPIClientTest')
    """
    logging: Logger instance
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
            with open("spw_config.json", "r") as json_file:
                json_data = json_file.read().replace("\n", "")
            self.config = json.loads(json_data)
        except IOError as err:
            self.LOGGER.error(
                "Unable to read configuration file: '%s'", err
        )



    def test_resolve_localhost(self):
        """
        Ensure that 'localhost' is resolved to a FQDN
        """
        self.api_spacewalk = SpacewalkAPIClient(
            logging.DEBUG, "localhost",
            self.config["config"]["api_user"],
            self.config["config"]["api_pass"]
        )
        #Ensure that we have two dots in the hostname
        hostname = self.api_spacewalk.get_hostname()
        self.assertTrue(
            hostname.count('.') == 2 and hostname != "localhost"
        )



    def test_resolve_shortname(self):
        """
        Ensure that short names are resolved to FQDNs
        """
        host_snip=self.config["config"]["hostname"]
        self.api_spacewalk = SpacewalkAPIClient(
            logging.DEBUG, host_snip[:host_snip.find('.')],
            self.config["config"]["api_user"],
            self.config["config"]["api_pass"]

        )
        #Ensure that we have two dots in the hostname
        hostname = self.api_spacewalk.get_hostname()
        self.assertTrue(
            hostname.count('.') == 2
        )



    def test_accept_fqdn(self):
        """
        Ensure that FQDNs are accepted
        """
        self.api_spacewalk = SpacewalkAPIClient(
            logging.DEBUG,
            self.config["config"]["hostname"],
            self.config["config"]["api_user"],
            self.config["config"]["api_pass"] 
        )
        #Ensure that we have two dots in the hostname
        hostname = self.api_spacewalk.get_hostname()
        self.assertTrue(
            hostname.count('.') == 2
        )



    def test_invalid_login(self):
        """
        Ensure exceptions on invalid logins
        """
        with self.assertRaises(InvalidCredentialsException):
            self.api_spacewalk = SpacewalkAPIClient(
                logging.DEBUG,
                self.config["config"]["hostname"],
                "giertz", "paulapinkepank"
            )



    def test_deny_legacy(self):
        """
        Ensure that old Spacewalk APIs are refused
        """
        #we really need to skip SSL verification for old versions
        ssl._create_default_https_context = ssl._create_unverified_context
        with self.assertRaises(APILevelNotSupportedException):
            self.api_spacewalk = SpacewalkAPIClient(
                logging.DEBUG, self.LEGACY_HOSTNAME,
                self.API_USER, self.API_PASS
            )



if __name__ == "__main__":
    #start tests or die in a fire
    if not os.path.isfile("spw_config.json"):
        print "Please create configuration file spw_config.json!"
        exit(1)
    else:
        #do not sort test cases as there are dependencies
        unittest.sortTestMethodsUsing = None
        unittest.main()
