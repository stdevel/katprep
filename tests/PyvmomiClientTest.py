#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Pyvmomi integration
"""

import os
import time
import unittest
import logging
import json
from katprep.clients.PyvmomiClient import PyvmomiClient
from katprep.clients import *

class PyvmomiClientTest(unittest.TestCase):
    """
    PyvmomiClient test cases
    """
    LOGGER = logging.getLogger('PyvmomiClientTest')
    """
    logging: Logger instance
    """
    pyvmomi_client = None
    """
    PyvmomiClient: Pyvmomi client
    """
    config = None
    """
    str: JSON object containing valid VMs
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
            with open("pyvmomi_config.json", "r") as json_file:
                json_data = json_file.read().replace("\n", "")
            self.config = json.loads(json_data)
        except IOError as err:
            self.LOGGER.error(
                "Unable to read configuration file: '%s'", err
            )
        #instance API client
        self.pyvmomi_client = PyvmomiClient(
            logging.ERROR, self.config["config"]["hostname"],
            self.config["config"]["api_user"],
            self.config["config"]["api_pass"]
        )

    #TODO
    #def hostname!!



    def test_valid_login(self):
        """
        Ensure exceptions on valid logins
        """
        #dummy call
        self.pyvmomi_client.get_vm_ips()

    def test_invalid_login(self):
        """
        Ensure exceptions on invalid logins
        """
        with self.assertRaises(SessionException):
            api_dummy = PyvmomiClient(
                logging.ERROR, self.config["config"]["hostname"],
                "giertz", "paulapinkepank"
            )
            #dummy call
            api_dummy.get_vm_ips()



if __name__ == "__main__":
    #start tests or die in a fire
    if not os.path.isfile("pyvmomi_config.json"):
        print "Please create configuration file pyvmomi_config.json!"
        exit(1)
    else:
        #do not sort test cases as there are dependencies
        unittest.sortTestMethodsUsing = None
        unittest.main()
