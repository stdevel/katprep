# -*- coding: utf-8 -*-
"""
Class for sending some very basic commands to Nagios/Icinga 1.x legacy
monitoring systems.
"""

import logging
import os
import re
import time
from datetime import datetime, timedelta

from lxml import html

from katprep.clients import SessionException, UnsupportedRequestException
from .base import HttpApiClient, MonitoringClientBase


class NagiosCGIClient(MonitoringClientBase, HttpApiClient):
    """
.. class:: NagiosCGIClient
    """
    LOGGER = logging.getLogger('NagiosCGIClient')
    """
    logging: Logger instance
    """
    HEADERS = {'User-Agent': 'katprep (https://github.com/stdevel/katprep)'}
    """
    dict: Default headers set for every HTTP request
    """
    obsolete = False
    """
    bool: Nagios system
    """

    def __init__(self, log_level, url, username, password, verify=True):
        """
        Constructor, creating the class. It requires specifying a
        URL. Optionally you can specify a username and password to access
        the API using HTTP Basic authentication.

        :param log_level: log level
        :type log_level: logging
        :param url: Nagios/Icinga URL
        :type url: str
        :param username: API username
        :type username: str
        :param password: corresponding password
        :type password: str
        """
        #set logging
        self.LOGGER.setLevel(log_level)
        if url[len(url)-1:] != "/":
            #add trailing slash
            url = "{}/".format(url)

        if "nagios" in url.lower():
            self.LOGGER.debug(
                "The 90s called, they want their monitoring system back"
            )
            self.set_nagios(True)


        super().__init__(url=url, username=username, password=password,
                         verify_ssl=verify)

    def set_nagios(self, flag):
        """
        This function sets a flag for Nagios systems as there are CGI
        differences between Nagios and Icinga 1.x.

        :param flag: boolean whether Nagios system
        :type flag: bool
        """
        self.obsolete = flag

    def _api_request(self, method, sub_url, payload=""):
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

.. seealso:: _api_get()
.. seealso:: _api_post()
        """
        #send request to API
        self.LOGGER.debug(
            "%s request to URL '%s', payload='%s'", method.upper(), sub_url, payload
        )
        try:
            if method.lower() not in ["get", "post"]:
                #going home
                raise SessionException("Illegal method '{}' specified".format(method))

            #execute request
            if method.lower() == "post":
                #POST
                result = self._session.post(
                    "{}{}".format(self._url, sub_url),
                    headers=self.HEADERS, data=payload, verify=self._verify_ssl
                    )
            else:
                #GET
                result = self._session.get(
                    "{}{}".format(self._url, sub_url),
                    headers=self.HEADERS, verify=self._verify_ssl
                    )
            #this really breaks shit
            #self.LOGGER.debug("HTML output: %s", result.text)
            if "error" in result.text.lower():
                tree = html.fromstring(result.text)
                data = tree.xpath(
                    "//div[@class='errorMessage']/text()"
                )
                raise SessionException("CGI error: {}".format(data[0]))
            if result.status_code in [401, 403]:
                raise SessionException("Unauthorized")
            elif result.status_code != 200:
                raise SessionException(
                    "{}: HTTP operation not successful".format(
                        result.status_code
                    )
                )
            else:
                #return result
                if method.lower() == "get":
                    return result.text
                else:
                    return True

        except ValueError as err:
            self.LOGGER.error(err)
            raise


    @staticmethod
    def calculate_time_range(hours):
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



    def _manage_downtime(
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
        (current_time, end_time) = self.calculate_time_range(hours)

        #set-up payload
        payload = {}
        if object_type.lower() == "hostgroup":
            if remove_downtime:
                #there is now way to unschedule downtime for a whole hostgroup
                raise UnsupportedRequestException(
                    "Unscheduling downtimes for whole hostgroups is not " \
                    "supported with Nagios/Icinga 1.x!"
                )
            else:
                payload[0] = {
                    'cmd_typ': '85', 'cmd_mod': '2', 'hostgroup': object_name,
                    'com_data': comment, 'trigger': '0', 'fixed': '1',
                    'hours': hours, 'minutes': '0', 'start_time': current_time,
                    'end_time': end_time, 'btnSubmit': 'Commit',
                    'com_author': self._username, 'childoptions': '0',
                    'ahas': 'on'
                }
        else:
            if remove_downtime:
                if self.obsolete:
                    #you really like old stuff don't you
                    raise UnsupportedRequestException(
                        "Unscheduling downtimes is not supported with Nagios!"
                    )
                else:
                    payload[0] = {
                        'cmd_typ': '171', 'cmd_mod': '2', 'host': object_name,
                        'btnSubmit': 'Commit'
                    }
            else:
                payload[0] = {
                    'cmd_typ': '86', 'cmd_mod': '2', 'host': object_name,
                    'com_data': comment, 'trigger': '0', 'fixed': '1',
                    'hours': hours, 'minutes': '0', 'start_time': current_time,
                    'end_time': end_time, 'btnSubmit': 'Commit',
                    'com_author': self._username, 'childoptions': '0'
                }
                if self.obsolete:
                    #we need to make two calls as legacy hurts twice
                    payload[1] = payload[0].copy()
                    payload[1]['cmd_typ'] = '55'

        #send POST
        result = None
        for req in payload:
            result = self._api_post("/cgi-bin/cmd.cgi", payload[req])
        return result



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
        return self._manage_downtime(object_name, object_type, hours, \
            comment, remove_downtime=False)



    def remove_downtime(self, object_name, object_type="host"):
        """
        Removes scheduled downtime for a host.
        For this, a object name is required.
        At this point, it is not possible to remove downtime for a
        whole hostgroup.

        :param object_name: Hostname or hostgroup name
        :type object_name: str
        """
        return self._manage_downtime(
            object_name, object_type, hours=1, comment="", remove_downtime=True
        )



    def has_downtime(self, object_name):
        """
        Returns whether a particular object (host, hostgroup) is currently in
        scheduled downtime. This required specifying an object name and type.

        :param object_name: Hostname or hostgroup name
        :type object_name: str
        """
        #retrieve host information
        result = self._api_get(
            "/cgi-bin/status.cgi?host={}".format(object_name)
        )
        #get _all_ the ugly images
        tree = html.fromstring(result)
        data = tree.xpath(
            "//td/a/img/@src"
        )

        #check whether downtime image was found
        downtime_imgs = ["downtime.gif"]
        for item in data:
            if os.path.basename(item) in downtime_imgs:
                return True
        return False



    @staticmethod
    def _regexp_matches(text, regexp):
        """
        Returns whether a text matches a particular regular expression.
        Used internally - isn't that funny outside get_services() or get_hosts().

        :param text: text
        :type text: str
        :param regexp: regular expression
        :type regexp: str

        """
        pattern = re.compile(regexp)
        return bool(pattern.match(text))



    @staticmethod
    def _is_blacklisted(text):
        """
        Returns whether a text received when parsing service information is
        blacklisted. Used internally - isn't that funny outside get_services().

        :param text: text
        :type text: str

        """
        #blacklisted strings
        blacklist = {
            "",
            "\n"
        }

        #blacklisted with regex:
        #1.Last check
        #2.State duration
        #3.Retries
        blacklist_regex = {
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}\s+[0-9]{2}:[0-9]{2}:[0-9]{2}",
            r"[0-9]{1,}d\s+[0-9]{1,}h\s+[0-9]{1,}m\s+[0-9]{1,}s",
            r"[0-9]{1,3}/[0-9]{1,3}"
        }
        if text not in blacklist:
            #compile _all_ the regexps!
            for item in blacklist_regex:
                #result = __regexp_matches(text, item)
                result = re.match(item, text)
                if result:
                    return True
            #good boy
            return False
        else:
            return True



    @staticmethod
    def _get_state(state):
        """
        Returns a numeric plugin return code based on the state

        :param state: plugin return string
        :type state: str
        """
        codes = {
            "unknown": 3.0, "critical": 2.0, "warning": 1.0, "ok": 0.0
        }
        for code in codes:
            if code in state[:8].lower():
                return codes[code]



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
        result = self._api_get(url)
        tree = html.fromstring(result)
        if only_failed:
            data = tree.xpath(
                "//td[@class='statusBGCRITICAL']/text() | "
                "//td[@class='statusBGCRITICAL']//a/text() | "
                "//td[@class='statusBGCRITICALSCHED']//text() | "
                "//td[@class='statusBGCRITICALSCHED']//a/text()"
            )
        else:
            data = tree.xpath(
                "//td[@class='statusOdd']/text() | "
                "//td[@class='statusOdd']//a/text() | "
                "//td[@class='statusEven']/text() | "
                "//td[@class='statusEven']//a/text() | "
                "//td[@class='statusBGCRITICAL']/text() | "
                "//td[@class='statusBGCRITICAL']//a/text() | "
                "//td[@class='statusBGCRITICALSCHED']//text() | "
                "//td[@class='statusBGCRITICALSCHED']//a/text()"
            )

        #only return service and extended status
        hits = []
        for item in data:
            item = item.lstrip()
            if not self._is_blacklisted(item):
                hits.append(item)
        #try building a beautiful array of dicts
        if len(hits)%2 != 0:
            services = []
            counter = 1
            while counter < len(hits):
                self.LOGGER.debug(
                    "Service '%s' has state '%s'", hits[counter], hits[counter+1]
                )
                services.append({
                    "name": hits[counter],
                    "state": self._get_state(hits[counter+1])
                })
                counter = counter + 2
            return services



    def get_hosts(self, ipv6_only=False):
        """
        Returns hosts by their name and IP.

        :param ipv6_only: use IPv6 addresses only
        :type ipv6_only: bool
        """
        #set-up URL
        url = "/cgi-bin/status.cgi?host=all&style=hostdetail&limit=0&start=1"
        #retrieve data
        result = self._api_get(url)
        tree = html.fromstring(result)
        #make sure to get the nested-nested table of the first table
        data = tree.xpath(
            "//table[@class='status']//tr//td[1]//table//td//table//td/a/text()"
        )
        #I want to punish the 'designer' of this 'HTML code'

        hosts = []
        for host in data:
            #get services per host

            #set-up URL
            url = "/cgi-bin/extinfo.cgi?type=1&host={}".format(host)
            #retrieve data
            result = self._api_get(url)
            #set-up xpath
            tree = html.fromstring(result)
            data = tree.xpath(
                "//div[@class='data']/text()"
            )

            #iterate through services
            target_ip = ""
            #NOTE: Nagios does not support IPv6, so we don't utilize the flag
            if ipv6_only:
                raise UnsupportedRequestException(
                    "IPv6 is not supported by Nagios/Icinga 1.x"
                )
            ip_regexp = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]" \
                r"|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4]" \
                r"[0-9]|25[0-5])$"
            for entry in data:
                if self._regexp_matches(entry, ip_regexp):
                    #entry is an IP
                    target_ip = entry
            this_host = {"name": host, "ip": target_ip}
            hosts.append(this_host)
        return hosts



    def is_authenticated(self):
        """
        This function is used for checking whether authorization succeeded.
        It simply retrieves status.cgi
        """
        #set-up URL
        url = "/cgi-bin/status.cgi?host=all&style=hostdetail&limit=0&start=1"
        #retrieve data
        result = self._api_get(url)
        return bool(result)
