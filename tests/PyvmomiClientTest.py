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
from katprep.clients import SessionException, InvalidCredentialsException, \
EmptySetException

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
    dummy_vm = "giertz.pinkepank.loc"
    """
    str: Non-existing VM
    """
    dummy_snapshot = "PyvmomiClientTest"
    """
    str: Snapshot title
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



    def test_valid_login(self):
        """
        Ensure exceptions on valid logins
        """
        #dummy call
        #TODO: other call?
        self.pyvmomi_client.get_vm_ips()

    def test_invalid_login(self):
        """
        Ensure exceptions on invalid logins
        """
        with self.assertRaises(InvalidCredentialsException):
            api_dummy = PyvmomiClient(
                logging.ERROR, self.config["config"]["hostname"],
                "giertz", "paulapinkepank"
            )
            #dummy call
            #TODO. other call?
            api_dummy.get_vm_ips()



    def test_create_snapshot(self):
        """
        Ensure that creating snapshots is possible
        """
        self.pyvmomi_client.create_snapshot(
            self.config["valid_objects"]["vm"],
            self.dummy_snapshot,
            self.dummy_snapshot
        )

    def test_create_snapshot_fail(self):
        """
        Ensure that creating snapshots of non-existing VMs is not possible
        """
        with self.assertRaises(SessionException):
            self.pyvmomi_client.create_snapshot(
                self.dummy_vm,
                self.dummy_snapshot,
                self.dummy_snapshot
            )

    def remove_snapshot(self):
        """
        Ensure that removing snapshots is possible
        """
        self.pyvmomi_client.remove_snapshot(
            self.config["valid_objects"]["vm"],
            self.dummy_snapshot
        )

    def test_remove_snapshot_fail(self):
        """
        Ensure that removing snapshots of non-existing VMs is not possible
        """
        with self.assertRaises(SessionException):
            self.pyvmomi_client.remove_snapshot(
                self.dummy_vm,
                self.dummy_snapshot
            )

    def revert_snapshot(self):
        """
        Ensure that reverting snapshots is possible
        """
        self.pyvmomi_client.revert_snapshot(
            self.config["valid_objects"]["vm"],
            self.dummy_snapshot
        )

    def test_revert_snapshot_fail(self):
        """
        Ensure that reverting non-existing snapshots is not possible
        """
        with self.assertRaises(SessionException):
            self.pyvmomi_client.revert_snapshot(
                self.dummy_vm,
                self.dummy_snapshot
            )

    def test_has_snapshot(self):
        """
        Ensure that checking for existing snapshots is possible
        """
        try:
            self.pyvmomi_client.has_snapshot(
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
            self.pyvmomi_client.has_snapshot(
                self.dummy_vm,
                self.dummy_snapshot
            )



    def test_get_vm_ips(self):
        """
        Ensure that receiving VMs with their IPs is possible
        """
        vm_ips = self.pyvmomi_client.get_vm_ips()
        self.assertTrue(
            self.config["valid_objects"]["vm"] in str(vm_ips)
        )

    def test_get_vm_hosts(self):
        """
        Ensure that receiving VMs with their hosts is possible
        """
        vm_hosts = self.pyvmomi_client.get_vm_hosts()
        self.assertTrue(
            self.config["valid_objects"]["vm"] in str(vm_hosts)
        )



    def test_restart_vm(self):
        """
        Ensure that restarting VMs is possible
        """
        self.pyvmomi_client.restart_vm(
            self.config["valid_objects"]["vm"]
        )
        time.sleep(10)

    def test_restart_vm_fail(self):
        """
        Ensure that restarting non-existing VMs is not possible
        """
        with self.assertRaises(SessionException):
            self.pyvmomi_client.restart_vm(
                self.dummy_vm
            )

    def test_restart_vm_forcefully(self):
        """
        Ensure that restarting VMs forcefully is possible
        """
        self.pyvmomi_client.restart_vm(
            self.config["valid_objects"]["vm"], force=True
        )
        time.sleep(10)

    def test_restart_vm_forcefully_fail(self):
        """
        Ensure that restarting non-existing VMs forcefully is not possible
        """
        with self.assertRaises(SessionException):
            self.pyvmomi_client.restart_vm(
                self.dummy_vm, force=True
            )



    def test_get_vm_powerstate(self):
        """
        Ensure that retrieving a VM's powerstate is possible
        """
        self.assertTrue(
            self.pyvmomi_client.powerstate_vm(
                self.config["valid_objects"]["vm"]
            ) in ["poweredOn", "poweredOff"]
        )

    def test_get_vm_powerstate_fail(self):
        """
        Ensure that retrieving a non-existent VM's powerstate is not possible
        """
        with self.assertRaises(SessionException):
            self.assertTrue(
                self.pyvmomi_client.powerstate_vm(
                    self.dummy_vm
                ) in ["poweredOn", "poweredOff"]
            )



    def vm_poweron(self):
        """
        Ensure that powering on a VM is possible
        """
        self.pyvmomi_client.poweron_vm(
            self.config["valid_objects"]["vm"]
        )
        time.sleep(10)

    def test_vm_poweron_fail(self):
        """
        Ensure that powering on a non-existing VM is not possible
        """
        with self.assertRaises(SessionException):
            self.pyvmomi_client.poweron_vm(
                self.dummy_vm
            )

    def vm_poweroff(self):
        """
        Ensure that powering off a VM is possible
        """
        self.pyvmomi_client.poweroff_vm(
            self.config["valid_objects"]["vm"]
        )
        time.sleep(10)

    def test_vm_poweroff_fail(self):
        """
        Ensure that powering off a non-existing VM is not possible
        """
        with self.assertRaises(SessionException):
            self.pyvmomi_client.poweroff_vm(
                self.dummy_vm
            )



if __name__ == "__main__":
    #start tests or die in a fire
    if not os.path.isfile("pyvmomi_config.json"):
        print "Please create configuration file pyvmomi_config.json!"
        exit(1)
    else:
        #do not sort test cases as there are dependencies
        unittest.sortTestMethodsUsing = None
        unittest.main()
