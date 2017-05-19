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
import re
from lxml import html

LOGGER = logging.getLogger('BasicNagiosCGIClient')



class BasicNagiosCGIClient:
    """
.. class:: BasicNagiosCGIClient
    """
    HEADERS = {'User-Agent': 'katprep (https://github.com/stdevel/katprep)'}
    """
    dict: Default headers set for every HTTP request
    """
    URL = ""
    """
    str: Nagios/Icinga URL
    """
    SESSION = None
    """
    session: API session
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
        #set connection details and connect
        self.URL = url
        self.USERNAME = username
        self.PASSWORD = password
        self.connect()



    def connect(self):
        """
        This function establishes a connection to Nagios/Icinga.
        """
        self.SESSION = requests.Session()
        if self.USERNAME != "":
            self.SESSION.auth = HTTPBasicAuth(self.USERNAME, self.PASSWORD)



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

.. seealso:: __api_get()
.. seealso:: __api_post()
        """
        #send request to API
        try:
            if method.lower() not in ["get", "post"]:
                #going home
                raise ValueError("Illegal method '{}' specified".format(method))

            #execute request
            if method.lower() == "post":
                #POST
                result = self.SESSION.post(
                    "{}{}".format(self.URL, sub_url),
                    headers=self.HEADERS, data=payload
                    )
            else:
                #GET
                result = self.SESSION.get(
                    "{}{}".format(self.URL, sub_url),
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
    def __api_get(self, sub_url):
        """
        Sends a HTTP GET request to the Nagios/Icinga API. This function
        requires a sub-URL (such as /cgi-bin/status.cgi).

        :param sub_url: relative path (e.g. /cgi-bin/status.cgi)
        :type sub_url: str
        """
        return self.api_request("get", sub_url)

    def __api_post(self, sub_url, payload):
        """
        Sends a HTTP POST request to the Nagios/Icinga API. This function
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
                'com_author': self.USERNAME, 'childoptions': '0', 'ahas': 'on'}
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
                    'com_author': self.USERNAME, 'childoptions': '0'}

        #send POST
        return self.__api_post("/cgi-bin/cmd.cgi", payload)



    def schedule_downtime(self, object_name, object_type, hours=8, \
        comment="Downtime managed by katprep"):
        """
        Adds scheduled downtime for a host or hostgroup.
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
        """
        return self.__manage_downtime(object_name, object_type, hours, \
            comment, remove_downtime=False)



    def remove_downtime(self, object_name):
        """
        Removes scheduled downtime for a host.
        For this, a object name is required.
        At this point, it is not possible to remove downtime for a
        whole hostgroup.

        :param object_name: Hostname or hostgroup name
        :type object_name: str
        """
        return __manage_downtime(object_name, "host", remove_downtime=True)



    def has_downtime(self, object_name):
        """
        Returns whether a particular object (host, hostgroup) is currently in
        scheduled downtime. This required specifying an object name and type.

        :param object_name: Hostname or hostgroup name
        :type object_name: str
        """
        #send GET
        result = self.__api_get(
            "/cgi-bin/status.cgi?host=all&hostprops=1&style=hostdetail")
        if object_name.lower() in str(result).lower():
            return True
        else:
            return False



    @staticmethod
    def __regexp_matches(text, regexp):
        """
        Returns whether a text matches a particular regular expression.
        Used internally - isn't that funny outside get_services() or get_hosts().

        :param text: text
        :type text: str
        :param regexp: regular expression
        :type regexp: str

        """
        pattern = re.compile(regexp)
        if pattern.match(text):
            return True
        else:
            return False



    @staticmethod
    def __is_blacklisted(text):
        """
        Returns whether a text received when parsing service information is
        blacklisted. Used internally - isn't that funny outside get_services().

        :param text: text
        :type text: str

        """
        #blacklisted strings
        blacklist = {"\n"}
        """
        blacklisted with regex:
        1.Last check
        2.State duration
        3.Retries
        """
        blacklist_regex = {
            "[0-9]{4}-[0-9]{2}-[0-9]{2}\s+[0-9]{2}:[0-9]{2}:[0-9]{2}",
            "[0-9]{1,}d\s+[0-9]{1,}h\s+[0-9]{1,}m\s+[0-9]{1,}s",
            "[0-9]{1,3}/[0-9]{1,3}"
        }
        if text not in blacklist:
            #compile _all_ the regexps!
            for item in blacklist_regex:
                result = __regexp_matches(text, item)
                if result:
                    return True
            #good boy
            return False
        else:
            return True



    def get_services(self, object_name, only_failed=True):
        """
        Returns all or failed services for a particular host.

        :param object_name:
        :type object_name: str
        :param only_failed: True will only report failed services
        :type only_failed: bool
        """

        #set-up URL
        url = "/cgi-bin/status.cgi?host={}&style=detail".format(object_name)
        if only_failed:
            url = "{}&hoststatustypes=15&servicestatustypes=16".format(url)
        #retrieve data
        result = self.__api_get(url)
        tree = html.fromstring(result)
        if only_failed:
            data = tree.xpath(
            "//td[@class='statusBGCRITICAL']/text() | "
            "//td[@class='statusBGCRITICAL']//a/text()"
            )
        else:
            #TODO: To ensure that this makes sense we need to add status
            #information to the result set...
            data = tree.xpath(
            "//td[@class='statusOdd']/text() | "
            "//td[@class='statusOdd']//a/text() | "
            "//td[@class='statusEven']/text() | "
            "//td[@class='statusEven']//a/text() | "
            "//td[@class='statusBGCRITICAL']/text() | "
            "//td[@class='statusBGCRITICAL']//a/text()"
            )

        #only return service and extended status
        hits = []
        for item in data:
            if not self.__is_blacklisted(item):
                hits.append(item)
        #try building a beautiful array of dicts
        if len(hits)%2 == 0:
            services = []
            counter = 0
            while counter < len(hits):
                services.append({hits[counter] : hits[counter+1]})
                counter = counter + 2
            return services
        return hits



    def get_hosts(self):
        """
        Returns hosts by their name and IP.
        """

        #set-up URL
        url = "/cgi-bin/status.cgi?host=all&style=hostdetail&limit=0&start=1"
        #retrieve data
        result = self.__api_get(url)
        tree = html.fromstring(result)
        data = tree.xpath(
        "//td[@class='statusHOSTPENDING']//a/text() |"
        "//td[@class='statusHOSTDOWNTIME']//a/text() |"
        "//td[@class='statusHOSTUP']//a/text() |"
        "//td[@class='statusHOSTDOWN']//a/text() |"
        "//td[@class='statusHOSTDOWNACK']//a/text() |"
        "//td[@class='statusHOSTDOWNSCHED']//a/text() |"
        "//td[@class='statusHOSTUNREACHABLE']//a/text() |"
        "//td[@class='statusHOSTUNREACHABLEACK']//a/text() |"
        "//td[@class='statusHOSTUNREACHABLESCHED']//a/text()"
        )
        
        hosts = []
        for host in data:
            #get services per host

            #set-up URL
            url = "/cgi-bin/extinfo.cgi?type=1&host={}".format(host)
            #retrieve data
            result = self.__api_get(url)
            #set-up xpath
            tree = html.fromstring(result)
            data = tree.xpath(
            "//div[@class='data']/text()"
            )

            #iterate through services
            ip = ""
            for entry in data:
                ip_regexp = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$";
                if self.__regexp_matches(entry, ip_regexp):
                    #entry is an IP
                    ip = entry
            this_host = {"name": host, "ip": ip}
            hosts.append(this_host)
        return hosts
