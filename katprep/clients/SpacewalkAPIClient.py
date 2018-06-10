#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file contains the SpacewalkAPIClient and
depending exception classes
"""

import logging
import socket
import xmlrpclib



class APILevelNotSupportedException(Exception):
    """
    Dummy class for unsupported API levels

.. class:: APILevelNotSupportedException
    """
    pass



class SessionException(Exception):
    """
    Dummy class for session errors

.. class:: SessionException
    """
    pass



class InvalidHostnameFormatException(Exception):
    """
    Dummy class for invalid hostname formats (non-FQDN)

.. class:: InvalidHostnameFormatException
    """
    pass



class InvalidCredentialsException(Exception):
    """
    Dummy class for invalid credentials

.. class:: InvalidCredentialsException
    """
    pass



class UnsupportedFilterException(Exception):
    """
    Dummy class for unsupported filters

.. class:: UnsupportedFilterException
    """
    pass



class SpacewalkAPIClient(object):
    """
    Class for communicating with the Spacewalk API

.. class:: SpacewalkAPIClient
    """
    LOGGER = logging.getLogger('SpacewalkAPIClient')
    """
    logging: Logger instance
    """
    API_MIN = "11.1"
    """
    int: Minimum supported API version.
    """
    HEADERS = {'User-Agent': 'katprep (https://github.com/stdevel/katprep)'}
    """
    dict: Default headers set for every HTTP request
    """
    hostname = ""
    """
    str: Spacewalk API hostname
    """
    url = ""
    """
    str: Spacewalk API base URL
    """
    username = ""
    """
    str: API username
    """
    password = ""
    """
    str: API password
    """
    api_session = None
    """
    Session: HTTP session to Spacewalk host
    """
    api_key = None
    """
    str: Session key
    """

    def __init__(self, log_level, hostname, username, password):
        """
        Constructor, creating the class. It requires specifying a
        hostname, username and password to access the API. After
        initialization, a connected is established.

        :param log_level: log level
        :type log_level: logging
        :param hostname: Spacewalk host
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
        self.hostname = self.validate_hostname(hostname)
        self.LOGGER.debug("Set hostname to '%s'", self.hostname)
        self.username = username
        self.password = password
        self.url = "https://{0}/rpc/api".format(self.hostname)

        #start session and check API version if Spacewalk API
        self.__connect()
        self.validate_api_support()



    def __exit__(self, exc_type, exc_value, traceback):
        """
        Destructor
        """
        self.api_session.auth.logout(self.api_key)



    def __connect(self):
        """
        This function establishes a connection to Spacewalk.
        """
        #set api session and key
        try:
            self.api_session = xmlrpclib.Server(self.url)
            self.api_key = self.api_session.auth.login(self.username, self.password)
        except xmlrpclib.Fault as err:
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
            api_level = self.api_session.api.getVersion()
            if api_level < self.API_MIN:
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



    @staticmethod
    def validate_hostname(hostname):
        """
        Validates that the Spacewalk API uses a FQDN as hostname.
        Also looks up the "real" hostname if "localhost" is specified.
        Otherwise, SSL won't work.

        :param hostname: the hostname to validate
        :type hostname: str
        """
        try:
            if hostname == "localhost":
                #get real hostname
                hostname = socket.gethostname()
            if hostname.count('.') != 2:
                #convert to FQDN if possible:
                hostname = socket.getaddrinfo(
                    socket.getfqdn(hostname), 0, 0, 0, 0,
                    socket.AI_CANONNAME
                )[0][3]
        except socket.gaierror:
            raise InvalidHostnameFormatException(
                "Unable to find FQDN for host '{}'".format(hostname)
            )
        return hostname



    def get_url(self):
        """
        Returns the configured URL of the object instance.
        """
        return self.url



    def get_hostname(self):
        """
        Returns the configured hostname of the objecti nstance.
        """
        return self.hostname
