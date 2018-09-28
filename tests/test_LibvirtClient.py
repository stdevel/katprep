#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Libvirt integration
"""

import os
import unittest
import logging
import json
from katprep.clients.LibvirtClient import LibvirtClient
from katprep.clients import SessionException, InvalidCredentialsException, \
EmptySetException

class LibvirtClientTest(unittest.TestCase):
    """
    LibvirtClient test cases
    """
    LOGGER = logging.getLogger('LibvirtClientTest')
    """
    logging: Logger instance
    """
    libvirt_client = None
    """
    LibvirtClient: Libvirt client
    """
    config = None
    """
    str: JSON object containing valid VMs
    """
    dummy_vm = "giertz.pinkepank.loc"
    """
    str: Non-existing VM
    """
    dummy_snapshot = "LibvirtClientTest"
    """
    str: Snapshot title
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
                with open("libvirt_config.json", "r") as json_file:
                    json_data = json_file.read().replace("\n", "")
                self.config = json.loads(json_data)
            except IOError as err:
                self.LOGGER.error(
                    "Unable to read configuration file: '%s'", err
                )
            #instance API client
            self.libvirt_client = LibvirtClient(
                logging.ERROR, self.config["config"]["uri"],
                self.config["config"]["api_user"],
                self.config["config"]["api_pass"]
            )
            self.set_up = True



    #def test_valid_login(self):
    #    """
    #    Ensure exceptions on valid logins
    #    """
    #    #dummy call
    #    #TODO: other call?
    #    self.libvirt_client.get_vm_ips()

    def test_invalid_login(self):
        """
        Ensure exceptions on invalid logins
        """
        with self.assertRaises(InvalidCredentialsException):
            api_dummy = LibvirtClient(
                logging.ERROR, self.config["config"]["uri"],
                "giertz", "paulapinkepank"
            )
            #dummy call
            #TODO: other call?
            #api_dummy.get_vm_ips()



    def test_create_snapshot(self):
        """
        Ensure that creating snapshots is possible
        """
        self.libvirt_client.create_snapshot(
            self.config["valid_objects"]["vm"],
            self.dummy_snapshot,
            self.dummy_snapshot
        )

    def test_create_snapshot_fail(self):
        """
        Ensure that creating snapshots of non-existing VMs is not possible
        """
        with self.assertRaises(SessionException):
            self.libvirt_client.create_snapshot(
                self.dummy_vm,
                self.dummy_snapshot,
                self.dummy_snapshot
            )

    def remove_snapshot(self):
        """
        Ensure that removing snapshots is possible
        """
        self.libvirt_client.remove_snapshot(
            self.config["valid_objects"]["vm"],
            self.dummy_snapshot
        )

    def test_remove_snapshot_fail(self):
        """
        Ensure that removing snapshots of non-existing VMs is not possible
        """
        with self.assertRaises(SessionException):
            self.libvirt_client.remove_snapshot(
                self.dummy_vm,
                self.dummy_snapshot
            )

    def revert_snapshot(self):
        """
        Ensure that reverting snapshots is possible
        """
        self.libvirt_client.revert_snapshot(
            self.config["valid_objects"]["vm"],
            self.dummy_snapshot
        )

    def test_revert_snapshot_fail(self):
        """
        Ensure that reverting non-existing snapshots is not possible
        """
        with self.assertRaises(SessionException):
            self.libvirt_client.revert_snapshot(
                self.dummy_vm,
                self.dummy_snapshot
            )

    def test_has_snapshot(self):
        """
        Ensure that checking for existing snapshots is possible
        """
        try:
            self.libvirt_client.has_snapshot(
                self.config["valid_objects"]["vm"],
                self.dummy_snapshot
            )
        except EmptySetException as err:
            pass

    def test_has_snapshot_fail(self):
        """
        Ensure that checking non-existing VMs for snapshots is not possible
        """
        with self.assertRaises(EmptySetException):
            self.libvirt_client.has_snapshot(
                self.dummy_vm,
                self.dummy_snapshot
            )



if __name__ == "__main__":
    #start tests or die in a fire
    if not os.path.isfile("libvirt_config.json"):
        print "Please create configuration file libvirt_config.json!"
        exit(1)
    else:
        #do not sort test cases as there are dependencies
        unittest.sortTestMethodsUsing = None
        unittest.main()
