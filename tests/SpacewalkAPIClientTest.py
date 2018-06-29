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
from katprep.clients import APILevelNotSupportedException, \
InvalidCredentialsException

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
                with open("spw_config.json", "r") as json_file:
                    json_data = json_file.read().replace("\n", "")
                self.config = json.loads(json_data)
                #TODO: Instance client
            except IOError as err:
                self.LOGGER.error(
                    "Unable to read configuration file: '%s'", err
                )
            self.set_up = True



    def test_invalid_login(self):
        """
        Ensure exceptions on invalid logins
        """
        with self.assertRaises(InvalidCredentialsException):
            self.api_spacewalk = SpacewalkAPIClient(
                logging.ERROR,
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
                logging.ERROR,
                self.config["config"]["hostname_legacy"],
                self.config["config"]["api_user"],
                self.config["config"]["api_pass"],
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
