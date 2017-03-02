#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Class for sending some very basic commands to Nagios/Icinga 1.x legacy
monitoring systems.
"""

import logging
import requests
from requests.auth import HTTPBasicAuth
import time
from datetime import datetime, timedelta

LOGGER = logging.getLogger('BasicNagiosCGIClient')



class BasicNagiosCGIClient:
    """
.. class:: BasicNagiosCGIClient
    """
    HEADERS = {'User-Agent': 'katprep (https://github.com/stdevel/katprep)'}
    """
    dict: Default headers set for every HTTP request
    """

    def __init__(self, url, username="", password=""):
        """
        Constructor, creating the class. It requires specifying a
        URL. Optionally you can specify a username and password to access
        the API using HTTP Basic authentication.

        :param url: Nagios/Icinga URL
        :type url: str
        :param username: API username
        :type username: str
        :param password: corresponding password
        :type password: str
        """
        if url[len(url)-1:] != "/":
            #add trailing slash
            url = "{}/".format(url)
        self.url = url
        self.username = username
        self.password = password

    def api_request(self, method, sub_url, payload=""):
        """
        Sends a HTTP request to the Nagios/Icinga API. This function requires
        a valid HTTP method and a sub-URL (such as /cgi-bin/status.cgi).
        Optionally, you can also specify payload (for POST).
        There are also alias functions available.

        :param method: HTTP request method (GET, POST)
        :type method: str
        :param sub_url: relative path (e.g. /cgi-bin/status.cgi)
        :type sub_url: str
        :param payload: payload for POST requests
        :type payload: str

.. seealso:: api_get()
.. seealso:: api_post()
        """
        #send request to API
        try:
            if method.lower() not in ["get", "post"]:
                #going home
                raise ValueError("Illegal method '{}' specified".format(method))

            #start session
            session = requests.Session()
            if self.username != "":
                session.auth = HTTPBasicAuth(self.username, self.password)

            #execute request
            if method.lower() == "post":
                #POST
                result = session.post(
                    "{}{}".format(self.url, sub_url),
                    headers=self.HEADERS, data=payload
                    )
            else:
                #GET
                result = session.get(
                    "{}{}".format(self.url, sub_url),
                    headers=self.HEADERS
                    )

            if "error" in result.text.lower():
                raise ValueError("Unable to authenticate")
            if result.status_code != 200:
                raise ValueError("{}: HTTP operation not successful".format(
                    result.status_code))
            else:
                #return result
                if method.lower() == "get":
                    return result.text
                else:
                    return True

        except ValueError as err:
            LOGGER.error(err)
            raise

    #Aliases
    def api_get(self, sub_url):
        """
        Sends a HTTP GET request to the Nagios/Icinga API. This function
        requires a sub-URL (such as /cgi-bin/status.cgi).

        :param sub_url: relative path (e.g. /cgi-bin/status.cgi)
        :type sub_url: str
        """
        return self.api_request("get", sub_url)

    def api_post(self, sub_url, payload):
        """
        Sends a HTTP GET request to the Nagios/Icinga API. This function
        requires a sub-URL (such as /cgi-bin/status.cgi).

        :param sub_url: relative path (e.g. /cgi-bin/status.cgi)
        :type sub_url: str
        :param payload: payload data
        :type payload: str
        """
        return self.api_request("post", sub_url, payload)



    def calculate_time(self, hours):
        """
        Calculates the time range for POST requests in the format the
        Nagios/Icinga 1.x API requires. For this, the current time/date
        is chosen and the specified amount of hours is added.

        :param hours: Amount of hours for the time range
        :type hours: int
        """
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        end_time = format(
            datetime.now() + timedelta(hours=int(hours)),
            '%Y-%m-%d %H:%M:%S')
        return (current_time, end_time)



    def manage_downtime(
            self, object_name, object_type, hours=8,
            comment="Downtime managed by katprep", remove_downtime=False
        ):
        """
        Adds or removes scheduled downtimes for hosts or hostgroups.
        For this, a object name and type are required.
        Optionally, you can specify a customized comment and downtime
        period (the default is 8 hours).

        :param object_name: Hostname or hostgroup name
        :type object_name: str
        :param object_type: host or hostgroup
        :type object_type: str
        :param hours: Amount of hours for the downtime (default: 8 hours)
        :type hours: int
        :param comment: Downtime comment
        :type comment: str
        :param remove_downtime: Removes a previously scheduled downtime
        :type remove_downtime: bool
        """
        #calculate timerange
        (current_time, end_time) = self.calculate_time(hours)

        #set-up payload
        if object_type.lower() == "hostgroup":
            #there is now way to unschedule downtime for a complete hostgroup
            payload = {
                'cmd_typ': '85', 'cmd_mod': '2', 'hostgroup': object_name,
                'com_data': comment, 'trigger': '0', 'fixed': '1',
                'hours': hours, 'minutes': '0', 'start_time': current_time,
                'end_time': end_time, 'btnSubmit': 'Commit',
                'com_author': self.username, 'childoptions': '0', 'ahas': 'on'}
        else:
            if remove_downtime:
                payload = {
                    'cmd_typ': '171', 'cmd_mod': '2', 'host': object_name,
                    'btnSubmit': 'Commit'}
            else:
                payload = {
                    'cmd_typ': '55', 'cmd_mod': '2', 'host': object_name,
                    'com_data': comment, 'trigger': '0', 'fixed': '1',
                    'hours': hours, 'minutes': '0', 'start_time': current_time,
                    'end_time': end_time, 'btnSubmit': 'Commit',
                    'com_author': self.username, 'childoptions': '0'}

        #send POST
        return self.api_post("/cgi-bin/cmd.cgi", payload)



    def has_downtime(self, object_name):
        """
        Returns whether a particular object (host, hostgroup) is currently in
        scheduled downtime. This required specifying an object name and type.

        :param object_name: Hostname or hostgroup name
        :type object_name: str
        """
        #send GET
        result = self.api_get(
            "/cgi-bin/status.cgi?host=all&hostprops=1&style=hostdetail")
        if object_name.lower() in str(result).lower():
            return True
        else:
            return False
