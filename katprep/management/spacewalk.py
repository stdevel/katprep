# -*- coding: utf-8 -*-
"""
This file contains the SpacewalkAPIClient and
depending exception classes
"""

import logging
from .base import BaseConnector
from .exceptions import (APILevelNotSupportedException, InvalidCredentialsException,
                         SessionException)

try:
    from xmlrpc.server import SimpleXMLRPCServer as Server
    from xmlrpc.client import Fault
except ImportError:
    from xmlrpclib import Server, Fault


class SpacewalkAPIClient(BaseConnector):
    """
    Class for communicating with the Spacewalk API

.. class:: SpacewalkAPIClient
    """
    LOGGER = logging.getLogger('SpacewalkAPIClient')
    """
    logging: Logger instance
    """
    API_MIN = 14.0
    """
    int: Minimum supported API version.
    """
    HEADERS = {'User-Agent': 'katprep (https://github.com/stdevel/katprep)'}
    """
    dict: Default headers set for every HTTP request
    """

    def __init__(self, log_level, hostname, username, password):
        """
        Constructor, creating the class. It requires specifying a
        hostname, username and password to access the API. After
        initialization, a connected is established.

        :param log_level: log level
        :type log_level: logging
        :param hostname: Spacewalk API hostname
        :type hostname: str
        :param username: API username
        :type username: str
        :param password: corresponding password
        :type password: str
        """
        #set logging
        logging.basicConfig(level=log_level)
        self.LOGGER.setLevel(log_level)
        self.LOGGER.debug(
            "About to create Spacewalk client '%s'@'%s'", username, hostname
        )

        #set connection information
        self.hostname = hostname
        self.LOGGER.debug("Set hostname to '%s'", self.hostname)
        self.username = username
        self.password = password
        self.url = "https://{0}/rpc/api".format(self.hostname)

        #start session and check API version if Spacewalk API
        self.api_key = None
        super().__init__(username, password)
        self.validate_api_support()



    def __exit__(self, exc_type, exc_value, traceback):
        """
        Destructor
        """
        self.api_session.auth.logout(self.api_key)



    def _connect(self):
        """
        This function establishes a connection to Spacewalk.
        """
        #set api session and key
        try:
            self._session = Server(self.url)
            self.api_key = self._session.auth.login(self._username, self._password)
        except Fault as err:
            if err.faultCode == 2950:
                raise InvalidCredentialsException(
                    "Wrong credentials supplied: '%s'", err.faultString
                )
            else:
                raise SessionException(
                    "Generic remote communication error: '%s'", err.faultString
                )



    def validate_api_support(self):
        """
        Checks whether the API version on the Spacewalk server is supported.
        Using older versions than 11.1 is not recommended. In this case, an
        exception will be thrown.
        """
        try:
            #check whether API is supported
            api_level = self._session.api.getVersion()
            if float(api_level) < self.API_MIN:
                raise APILevelNotSupportedException(
                    "Your API version ({0}) does not support the required calls. "
                    "You'll need API version ({1}) or higher!".format(
                        api_level, self.API_MIN
                    )
                )
            else:
                self.LOGGER.info("Supported API version (" + api_level + ") found.")
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
