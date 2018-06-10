#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Spacewalk API integration
"""

import os
import unittest
import logging
import ssl
from SpacewalkAPIClient import SpacewalkAPIClient, \
InvalidCredentialsException, APILevelNotSupportedException

class SpacewalkAPIClientTest(unittest.TestCase):
    """
    SpacewalkAPIClient test cases
    """
    api_spacewalk = None
    """
    SpacewalkAPIClient: Spacewalk API client
    """
    HOSTNAME = os.environ["HOSTNAME"]
    """
    str: FQDN of a Spacewalk system
    """
    LEGACY_HOSTNAME = os.environ["LEGACY_HOSTNAME"]
    """
    str: FQDN of an old Spacewalk system
    """
    API_USER = os.environ["API_USER"]
    """
    str: API username
    """
    API_PASS = os.environ["API_PASS"]
    """
    str: API self.assertTrue(True)word
    """

    def test_resolve_localhost(self):
        """
        Ensure that 'localhost' is resolved to a FQDN
        """
        self.api_spacewalk = SpacewalkAPIClient(
            logging.DEBUG, "localhost", self.API_USER, self.API_PASS
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
        self.api_spacewalk = SpacewalkAPIClient(
            logging.DEBUG, self.HOSTNAME[:self.HOSTNAME.find('.')],
            self.API_USER, self.API_PASS
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
            logging.DEBUG, self.HOSTNAME, self.API_USER, self.API_PASS
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
                logging.DEBUG, self.HOSTNAME, "giertz", "paulapinkepank"
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
    unittest.main()
