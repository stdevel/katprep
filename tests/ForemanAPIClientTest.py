#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Foreman API integration
"""

import os
import unittest
import logging
import json
import random
from katprep.clients.ForemanAPIClient import ForemanAPIClient
from katprep.clients import SessionException

class ForemanAPIClientTest(unittest.TestCase):
    """
    ForemanAPIClient test cases
    """
    LOGGER = logging.getLogger('ForemanAPIClientTest')
    """
    logging: Logger instance
    """
    api_foreman = None
    """
    ForemanAPIClient: Foreman API client
    """
    config = None
    """
    str: JSON object containing valid hostgroup, location, organization,
    environment and host objects
    """
    bookmark_id = 0
    """
    int: ID of temporary bookmark
    """
    set_up = False
    """
    bool: Flag whether the connection was set up
    """



    def setUp(self):
        """
        Connecting the interface and populating demo content
        """
        #only set-up _all_ the stuff once
        if not self.set_up:
            #instance logging
            logging.basicConfig()
            self.LOGGER.setLevel(logging.DEBUG)
            #reading configuration
            try:
                with open("fman_config.json", "r") as json_file:
                    json_data = json_file.read().replace("\n", "")
                self.config = json.loads(json_data)
            except IOError as err:
                self.LOGGER.error(
                    "Unable to read configuration file: '%s'", err
                )
            #connect to API
            self.api_foreman = ForemanAPIClient(
                logging.ERROR, self.config["config"]["hostname"],
                self.config["config"]["api_user"],
                self.config["config"]["api_pass"],
                verify=False
            )
            #create demo bookmark
            try:
                self.api_foreman.api_post(
                    "/bookmarks", '''
                        {
                            "bookmark":
                            {
                                "name": "ForemanAPIClientTest",
                                "controller": "dashboard",
                                "query": "architecture = x86_64",
                                "public": true
                            }
                        }'''
                )
            except SessionException as err:
                if "422" in err:
                    #demo content already present
                    pass
            #Retrieving the ID of the previously created bookmark
            bookmarks = json.loads(
                self.api_foreman.api_get(
                    "/bookmarks"
                )
            )
            for bookmark in bookmarks["results"]:
                if bookmark["name"] == "ForemanAPIClientTest":
                    self.bookmark_id = bookmark["id"]
        self.set_up = True

    def tearDown(self):
        """
        Ensure to remove demo content if not removed, yet
        """
        try:
            self.api_foreman.api_delete(
                "/bookmarks/{}".format(self.bookmark_id), ""
            )
        except SessionException as err:
            if "404" in err:
                #demo content already removed
                pass



    def test_valid_login(self):
        """
        Ensure exceptions on valid logins
        """
        #dummy call
        self.api_foreman.api_get("/architectures")

    def invalid_login(self):
        """
        Ensure exceptions on invalid logins
        """
        with self.assertRaises(SessionException):
            api_dummy = ForemanAPIClient(
                logging.ERROR, self.config["config"]["hostname"],
                "giertz", "paulapinkepank",
                verify=False
            )
            #dummy call
            api_dummy.api_get("/status")



    #def test_deny_legacy(self):



    #TODO: remove after Spacewalk support (mark as private function)
    def api_post(self):
        """
        Ensure that GET calls are working
        """
        #Creating a dummy bookmark
        self.api_foreman.api_post(
            "/bookmarks", '''
                {
                    "bookmark":
                    {
                        "name": "ForemanAPIClientTest",
                        "controller": "dashboard",
                        "query": "architecture = x86_64",
                        "public": true
                    }
                }'''
        )

    def test_api_get(self):
        """
        Ensure that GET calls are working
        """
        bookmarks = json.loads(
            self.api_foreman.api_get(
                "/bookmarks/{}".format(self.bookmark_id)
            )
        )
        self.assertTrue(
            bool(str(bookmarks) != "")
        )

    def test_api_put(self):
        """
        Ensure that PUT calls are working
        """
        self.api_foreman.api_put(
            "/bookmarks/{}".format(self.bookmark_id), '''
                {
                    "bookmark": {
                        "name": "ForemanAPIClientTest",
                        "controller": "dashboard",
                        "query": "architecture = i386"
                    }
                }'''
        )

    def test_api_delete(self):
        """
        Ensure that DELETE calls are working
        """
        self.api_foreman.api_delete(
            "/bookmarks/{}".format(self.bookmark_id), ""
        )

    def test_api_invalid(self):
        """
        Ensure that dumbass calls will fail
        """
        with self.assertRaises(SessionException):
            self.api_foreman.api_get("/giertz/stdevel")



    def test_get_name_by_id(self):
        """
        Ensure that names can be retrieved by supplying an ID
        """
        for f_obj, f_conf in self.config["valid_objects"].iteritems():
            self.assertTrue(
                bool(
                    self.api_foreman.get_name_by_id(f_conf['id'], f_obj)
                )
            )

    def test_get_name_by_id_invalid(self):
        """
        Ensure that names cannot be retrieving when supplying invalid IDs
        """
        with self.assertRaises(SessionException):
            for f_obj, f_conf in self.config["valid_objects"].iteritems():
                self.assertTrue(
                    bool(
                        self.api_foreman.get_name_by_id(
                            random.randint(800, 1500), f_obj
                        )
                    )
                )



    def test_get_id_by_name(self):
        """
        Ensure that IDs can be retrieved by supplying an ID
        """
        for f_obj, f_conf in self.config["valid_objects"].iteritems():
            self.assertTrue(
                bool(
                    self.api_foreman.get_id_by_name(f_conf['name'], f_obj)
                )
            )

    def test_get_id_by_name_invalid(self):
        """
        Ensure that names IDs cannot be retrieved by supplying invalid IDs
        """
        with self.assertRaises(SessionException):
            for f_obj, f_conf in self.config["valid_objects"].iteritems():
                self.api_foreman.get_id_by_name(
                    "giertz{}".format(random.randint(800, 1500)), f_obj
                )



    def test_get_hostparams(self):
        """
        Ensure that host params can be retrieved
        """
        hostparams = self.api_foreman.get_host_params(
            self.config["valid_objects"]["host"]["id"]
        )
        self.assertTrue(
            bool(str(hostparams) != "")
        )

    def test_get_hostparams_invalid(self):
        """
        Ensure that host params cannot be retrieved by supplying invalid IDs
        """
        with self.assertRaises(SessionException):
            hostparams = self.api_foreman.get_host_params(
                random.randint(800, 1500)
            )
            self.assertTrue(
                bool(str(hostparams) != "")
            )

    #TODO: after Spacewalk support:
    #create/update/remove hostparam



if __name__ == "__main__":
    #start tests or die in a fire
    if not os.path.isfile("fman_config.json"):
        print "Please create configuration file fman_config.json!"
        exit(1)
    else:
        unittest.main()
