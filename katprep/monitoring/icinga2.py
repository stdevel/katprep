# -*- coding: utf-8 -*-
"""
Class for sending some very basic commands to Icinga 2.x
monitoring systems.
"""

import json
import logging
from datetime import datetime, timedelta

from .base import DOWNTIME_COMMENT, HttpApiClient, MonitoringClientBase
from ..exceptions import EmptySetException, SessionException


class Icinga2APIClient(MonitoringClientBase, HttpApiClient):
    """
    Class for communicating with the Icinga2 API

    .. class:: Icinga2APIClient
    """

    LOGGER = logging.getLogger("Icinga2APIClient")
    """
    logging: Logger instance
    """
    HEADERS = {
        "User-Agent": "katprep (https://github.com/stdevel/katprep)",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    """
    dict: Default headers set for every HTTP request
    """

    def __init__(self, log_level, url, username="", password="", verify_ssl=False):
        """
        Constructor, creating the class. It requires specifying a
        URL, an username and password to access the API.

        :param log_level: log level
        :type log_level: logging
        :param url: Icinga URL
        :type url: str
        :param username: API username
        :type username: str
        :param password: corresponding password
        :type password: str
        """
        # set logging
        self.LOGGER.setLevel(log_level)

        if "/v1" not in url:
            url = "{}/v1".format(url)

        super().__init__(
            url=url, username=username, password=password, verify_ssl=verify_ssl
        )

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
        """
        # send request to API
        try:
            if method.lower() not in ["get", "post"]:
                # going home
                raise SessionException("Illegal method '{}' specified".format(method))
            self.LOGGER.debug(
                "%s request to %s (payload: %s)", method.upper(), sub_url, payload
            )

            # execute request
            if method.lower() == "post":
                # POST
                result = self._session.post(
                    "{}{}".format(self._url, sub_url),
                    headers=self.HEADERS,
                    data=payload,
                    verify=self._verify_ssl,
                )
            else:
                # GET
                result = self._session.get(
                    "{}{}".format(self._url, sub_url),
                    headers=self.HEADERS,
                    verify=self._verify_ssl,
                )

            if result.status_code == 404:
                raise EmptySetException("HTTP resource not found: {}".format(sub_url))
            elif result.status_code != 200:
                raise SessionException(
                    "{}: HTTP operation not successful".format(result.status_code)
                )

            # return result
            self.LOGGER.debug(result.text)
            return result
        except ValueError as err:
            self.LOGGER.error(err)
            raise SessionException(err)

    @staticmethod
    def calculate_time_range(hours):
        """
        Calculates the time range for POST requests in the format the
        Icinga 2.x API requires. For this, the current time/date
        is chosen and the specified amount of hours is added.

        :param hours: Amount of hours for the time range
        :type hours: int
        """
        current_time = datetime.now()
        end_time = current_time + timedelta(hours=int(hours))
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
        # calculate timerange
        (current_time, end_time) = self.calculate_time_range(hours)

        if object_type.lower() == "hostgroup":
            if remove_downtime:
                # remove hostgroup downtime
                payload = {
                    "type": "Host",
                    "filter": '"{}" in host.groups'.format(object_name),
                }
            else:
                # create hostgroup downtime
                payload = {
                    "type": "Host",
                    "filter": '"{}" in host.groups'.format(object_name),
                    "start_time": current_time.timestamp(),
                    "end_time": end_time.timestamp(),
                    "fixed": True,
                    "author": self._username,
                    "comment": comment,
                }
        else:
            if remove_downtime:
                # remove host downtime
                payload = {
                    "type": "Host",
                    "filter": 'host.name=="{}"'.format(object_name),
                }
            else:
                # create host downtime
                payload = {
                    "type": "Host",
                    "filter": 'host.name=="{}"'.format(object_name),
                    "start_time": current_time.timestamp(),
                    "end_time": end_time.timestamp(),
                    "fixed": True,
                    "author": self._username,
                    "comment": comment,
                }

        # send POST
        result = ""
        if remove_downtime:
            payload["type"] = "Host"
            result = self._api_post("/actions/remove-downtime", json.dumps(payload))
            payload["type"] = "Service"
            result = self._api_post("/actions/remove-downtime", json.dumps(payload))
        else:
            payload["type"] = "Host"
            result = self._api_post("/actions/schedule-downtime", json.dumps(payload))
            payload["type"] = "Service"
            result = self._api_post("/actions/schedule-downtime", json.dumps(payload))

        # return result
        result_obj = json.loads(result.text)
        if len(result_obj["results"]) == 0:
            raise EmptySetException("Host/service not found")

        return result

    def schedule_downtime(
        self, object_name, object_type, hours=8, comment=DOWNTIME_COMMENT
    ):
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
        return self._manage_downtime(
            object_name, object_type, hours, comment, remove_downtime=False
        )

    def remove_downtime(self, object_name, object_type):
        """
        Removes scheduled downtime for a host or hostgroup
        For this, a object name is required.

        :param object_name: Hostname or hostgroup name
        :type object_name: str
        :param object_type: host or hostgroup
        :type object_type: str
        """
        return self._manage_downtime(
            object_name,
            object_type,
            8,
            "Downtime managed by katprep",
            remove_downtime=True,
        )

    def has_downtime(self, object_name, object_type="host"):
        """
        Returns whether a particular object (host, hostgroup) is currently in
        scheduled downtime. This required specifying an object name and type.

        :param object_name: Hostname or hostgroup name
        :type object_name: str
        :param object_type: Host or hostgroup (default: host)
        :type object_type: str
        """
        # retrieve and load data
        try:
            result = self._api_get(
                "/objects/{}s?host={}".format(object_type, object_name)
            )
            data = json.loads(result.text)
            # check if downtime
            # TODO: how to do this for hostgroups?!
            if object_type == "host":
                for result in data["results"]:
                    if result["attrs"]["downtime_depth"] > 0:
                        return True
                return False
        except SessionException as err:
            if "404" in err.message:
                raise EmptySetException("Host not found")

    def get_services(self, object_name, only_failed=True):
        """
        Returns all or failed services for a particular host.

        :param object_name:
        :type object_name: str
        :param only_failed: True will only report failed services
        :type only_failed: bool
        """
        # retrieve result
        result = self._api_get(
            '/objects/services?filter=match("{}",host.name)'.format(object_name)
        )
        data = json.loads(result.text)
        services = []
        for result in data["results"]:
            # get all the service information
            service = result["attrs"]["display_name"]
            state = result["attrs"]["state"]
            self.LOGGER.debug("Found service '%s' with state '%s'", service, state)
            if not only_failed or float(state) != 0.0:
                # append service if ok or state not ok
                this_service = {"name": service, "state": state}
                services.append(this_service)

        if len(services) == 0:
            # empty set
            raise EmptySetException("No results for host {!r}".format(object_name))

        return services

    def get_hosts(self, ipv6_only=False):
        """
        Returns hosts by their name and IP.

        :param ipv6_only: use IPv6 addresses only
        :type ipv6_only: bool
        """
        # retrieve result
        result = self._api_get("/objects/hosts")
        data = json.loads(result.text)
        hosts = []
        for result in data["results"]:
            # get all the host information
            host = result["attrs"]["display_name"]
            if ipv6_only:
                ip = result["attrs"]["address6"]
            else:
                ip = result["attrs"]["address"]
            this_host = {"name": host, "ip": ip}
            hosts.append(this_host)

        return hosts

    def is_authenticated(self):
        """
        This function is used for checking whether authorization succeeded.
        It simply retrieves status.cgi
        """
        result = self._api_get("/")
        return bool(result)
