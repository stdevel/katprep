#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Uyuni XMLRPC API client
"""

import logging
from xmlrpc.client import ServerProxy, Fault
import ssl
from katprep.clients import (SessionException, InvalidCredentialsException,
                             APILevelNotSupportedException,
                             SSLCertVerificationError,
                             EmptySetException)


class UyuniAPIClient:
    """
    Class for communicating with the Uyuni API

.. class:: UyuniAPIClient
    """
    LOGGER = logging.getLogger('UyuniAPIClient')
    """
    logging: Logger instance
    """
    API_MIN = 22
    """
    int: Minimum supported API version.
    """
    HEADERS = {'User-Agent': 'katprep (https://github.com/stdevel/katprep)'}
    """
    dict: Default headers set for every HTTP request
    """
    hostname = ""
    """
    str: Uyuni API hostname
    """
    url = ""
    """
    str: Uyuni API base URL
    """
    username = ""
    """
    str: API username
    """
    password = ""
    """
    str: API password
    """
    port = 443
    """
    int: HTTPS port
    """
    skip_ssl = False
    """
    bool: Flag whether to ignore SSL verification
    """
    api_session = None
    """
    Session: HTTP session to Uyuni host
    """
    api_key = None
    """
    str: Session key
    """

    def __init__(
            self, log_level, hostname, username, password,
            port, skip_ssl=False
    ):
        """
        Constructor creating the class. It requires specifying a
        hostname, username and password to access the API. After
        initialization, a connected is established.

        :param log_level: log level
        :type log_level: logging
        :param hostname: Uyuni host
        :type hostname: str
        :param username: API username
        :type username: str
        :param password: corresponding password
        :type password: str
        :param port: HTTPS port
        :type port: int
        """
        # set logging
        logging.basicConfig(level=log_level)
        self.LOGGER.setLevel(log_level)
        self.LOGGER.debug(
            "About to create Uyuni client '%s'@'%s'", username, hostname
        )

        # set connection information
        self.hostname = hostname
        self.LOGGER.debug("Set hostname to '%s'", self.hostname)
        self.username = username
        self.password = password
        self.port = port
        self.url = "https://{0}:{1}/rpc/api".format(self.hostname, self.port)
        self.skip_ssl = skip_ssl

        # start session and check API version if Uyuni API
        self.__connect()
        self.validate_api_support()

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Destructor
        """
        self.api_session.auth.logout(self.api_key)

    def __connect(self):
        """
        This function establishes a connection to Uyuni.
        """
        # set API session and key
        try:
            if self.skip_ssl:
                context = ssl._create_unverified_context()
            else:
                context = ssl.create_default_context()

            self.api_session = ServerProxy(self.url, context=context)
            self.api_key = self.api_session.auth.login(
                self.username, self.password
                )
        except ssl.SSLCertVerificationError as err:
            self.LOGGER.error(err)
            raise SSLCertVerificationError
        except Fault as err:
            if err.faultCode == 2950:
                raise InvalidCredentialsException(
                    "Wrong credentials supplied: '%s'" % err.faultString
                )
            raise SessionException(
                "Generic remote communication error: '%s'"
                % err.faultString
            )

    def validate_api_support(self):
        """
        Checks whether the API version on the Uyuni server is supported.
        Using older versions than 24 is not recommended. In this case, an
        exception will be thrown.
        """
        try:
            # check whether API is supported
            api_level = self.api_session.api.getVersion()
            if float(api_level) < self.API_MIN:
                raise APILevelNotSupportedException(
                    "Your API version ({0}) doesn't support required calls."
                    "You'll need API version ({1}) or higher!".format(
                        api_level, self.API_MIN
                    )
                )
            self.LOGGER.info("Supported API version %s found.", api_level)
        except ValueError as err:
            self.LOGGER.error(err)
            raise APILevelNotSupportedException("Unable to verify API version")

    def get_url(self):
        """
        Returns the configured URL of the object instance.
        """
        return self.url

    def get_hostname(self):
        """
        Returns the configured hostname of the object instance.
        """
        return self.hostname

    def get_host_id(self, hostname):
        """
        Returns the profile ID of a particular system
        """
        try:
            host_id = self.api_session.system.getId(self.api_key, hostname)
            if len(host_id) > 0:
                return host_id[0]["id"]
            raise EmptySetException(
                "System not found: '%s'"
                % hostname
            )
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise EmptySetException(
                    "System not found: '%s'"
                    % hostname
                )
            raise SessionException(
                "Generic remote communication error: '%s'"
                % err.faultString
            )

    def get_host_params(self, system_id):
        """
        Returns the parameters of a particular system
        """
        try:
            params = self.api_session.system.getCustomValues(
                self.api_key, system_id
                )
            return params
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    "System not found: '%s'"
                    % system_id
                )
            raise SessionException(
                "Generic remote communication error: '%s'"
                % err.faultString
            )
