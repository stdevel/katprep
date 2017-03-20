#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Class for sending some very basic commands to Icinga 2.x
monitoring systems.
"""

import logging
import requests
#from requests.auth import HTTPBasicAuth
#import time
#from datetime import datetime, timedelta
#import re
#from lxml import html

LOGGER = logging.getLogger('BasicIcinga2APIClient')



class BasicIcinga2APIClient:
    """
.. class:: BasicIcinga2APIClient
    """
    HEADERS = {'User-Agent': 'katprep (https://github.com/stdevel/katprep)'}
    """
    dict: Default headers set for every HTTP request
    """
    SESSION = None
    """
    session: API session
    """

    def __init__(self, url, username="", password=""):
        """
        Constructor, creating the class. It requires specifying a
        URL, an username and password to access the API.

        :param url: Icinga URL
        :type url: str
        :param username: API username
        :type username: str
        :param password: corresponding password
        :type password: str
        """
        if url[len(url)-1:] != "/":
            #add trailing slash
            url = "{}/".format(url)
        #set connection details and connect
        self.URL = url
        self.USERNAME = username
        self.PASSWORD = password
        self.connect()



    def connect(self):
        """
        This function establishes a connection to Icinga 2.
        """
        print "TODO: connect"



    def api_request(self):
        """
        Sends a HTTP request to the Nagios/Icinga API. This function requires
        a valid HTTP method and a sub-URL (such as /cgi-bin/status.cgi).
        Optionally, you can also specify payload (for POST).
        There are also alias functions available.
        """
        print "TODO: request"



    def __manage_downtime(
            self, object_name, object_type, hours, comment, remove_downtime
        ):
        """
        Adds or removes scheduled downtime for a host or hostgroup.
        For this, a object name and type are required.
        You can also specify a comment and downtime period.

        :param object_name: Hostname or hostgroup name
        :type object_name: str
        :param object_type: host or hostgroup
        :type object_type: str
        :param hours: Amount of hours for the downtime
        :type hours: int
        :param comment: Downtime comment
        :type comment: str
        :param remove_downtime: Removes a previously scheduled downtime
        :type remove_downtime: bool
        """
        print "TODO: manage downtime"



    def schedule_downtime(self):
        """
        Adds scheduled downtime for a host or hostgroup.
        For this, a object name and type are required.
        Optionally, you can specify a customized comment and downtime
        period (the default is 8 hours).
        """
        print "TODO: schedule downtime"



    def remove_downtime(self):
        """
        Removes scheduled downtime for a host.
        For this, a object name is required.
        At this point, it is not possible to remove downtime for a
        whole hostgroup.
        """
        print "TODO: remove downtime"



    def has_downtime(self, object_name):
        """
        Returns whether a particular object (host, hostgroup) is currently in
        scheduled downtime. This required specifying an object name and type.
        """
        print "TODO: has downtime"



    def get_services(self, object_name, only_failed=True):
        """
        Returns all or failed services for a particular host.
        """
        print "TODO: get_services"
