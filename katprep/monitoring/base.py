# -*- coding: utf-8 -*-
"""
A basic monitoring client.
"""

from abc import ABCMeta, abstractmethod

from requests import Session
from requests.auth import HTTPBasicAuth

from ..exceptions import UnauthenticatedError

DOWNTIME_COMMENT = "Downtime managed by katprep"


class MonitoringClientBase(metaclass=ABCMeta):
    """
    Base class for creating an monitoring client.
    """

    @abstractmethod
    def schedule_downtime(self, obj, hours=8, comment=DOWNTIME_COMMENT):
        """
        Adds scheduled downtime for a host or hostgroup.
        For this, a object name and type are required.
        Optionally, you can specify a customized comment and downtime
        period (the default is 8 hours).

        :param obj: Host or hostgroup to manage
        :type obj: Host or HostGroup
        :param hours: Amount of hours for the downtime (default: 8 hours)
        :type hours: int
        :param comment: Downtime comment
        :type comment: str
        """

    @abstractmethod
    def remove_downtime(self, obj):
        """
        Removes scheduled downtime for a host or hostgroup
        For this, a object name is required.

        :param obj: Host or hostgroup to manage
        :type obj: Host or HostGroup
        """

    @abstractmethod
    def has_downtime(self, obj):
        """
        Returns whether a particular object host is currently in scheduled
        downtime.

        :param obj: Host to check
        :type obj: Host
        """

    @abstractmethod
    def get_hosts(self, ipv6_only=False):
        """
        Returns hosts by their name and IP.

        :param ipv6_only: use IPv6 addresses only
        :type ipv6_only: bool
        """

    @abstractmethod
    def get_services(self, obj, only_failed=True):
        """
        Returns all or failed services for a particular host.

        :param obj: Host to get services from
        :type obj: Host
        """


class HttpApiClient:
    """
    Base client for HTTP API interaction.

    The functions `_api_get` and `_api_post` are aliases for easier use.
    """

    def __init__(self, url, username=None, password=None, verify_ssl=True):
        """
        Create a new API client.

        If username and password are given HTTP basic authentication
        will be used.

        :param url: The API URL
        :type url: str
        :param username: API username
        :type username: str
        :param password: corresponding password
        :type password: str
        :param verify_ssl: Control SSL verfication.
        :type verify_ssl: bool
        """
        self._url = url
        self._username = username
        self._password = password
        self._verify_ssl = verify_ssl
        self._session = None

        self._connect()

    def _connect(self):
        """
        This function establishes a connection to the Icinga2 API.
        """
        self._session = Session()

        if self._username:
            self._session.auth = HTTPBasicAuth(self._username, self._password)

        if not self.is_authenticated():
            raise UnauthenticatedError("Unable to authenticate!")

    @abstractmethod
    def is_authenticated(self):
        """
        Check if authentication against the API works.

        :rtype: bool
        """

    @abstractmethod
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

    # Aliases
    def _api_get(self, sub_url):
        """
        Sends a HTTP GET request to the API.
        This function requires a sub-URL (such as /cgi-bin/status.cgi).

        :param sub_url: relative path (e.g. /cgi-bin/status.cgi)
        :type sub_url: str
        """
        return self._api_request("get", sub_url)

    def _api_post(self, sub_url, payload):
        """
        Sends a HTTP POST request to the API.
        This function requires a sub-URL (such as /cgi-bin/status.cgi).

        :param sub_url: relative path (e.g. /cgi-bin/status.cgi)
        :type sub_url: str
        :param payload: payload data
        :type payload: str
        """
        return self._api_request("post", sub_url, payload)
